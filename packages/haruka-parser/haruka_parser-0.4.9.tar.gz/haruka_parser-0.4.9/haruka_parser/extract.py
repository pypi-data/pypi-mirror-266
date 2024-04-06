import os
import re
import unicodedata
from collections import defaultdict
from typing import Dict
from haruka_parser.readablity_lxml import Document, get_html
from resiliparse.parse.html import HTMLTree
from resiliparse.extract.html2text import extract_plain_text
from inscriptis import ParserConfig
from inscriptis.css_profiles import CSS_PROFILES
from inscriptis.html_engine import Inscriptis
from inscriptis.model.html_document_state import HtmlDocumentState
from inscriptis.model.tag.a_tag import a_start_handler, a_end_handler
from inscriptis.model.tag.br_tag import br_start_handler
from inscriptis.model.tag.img_tag import img_start_handler
from inscriptis.model.tag.list_tag import (
    ul_start_handler,
    ol_start_handler,
    li_start_handler,
    ul_end_handler,
    ol_end_handler,
)
from inscriptis.model.tag.table_tag import (
    table_start_handler,
    tr_start_handler,
    td_start_handler,
    table_end_handler,
    td_end_handler,
)
import ftfy
from inscriptis.model.tag import CustomHtmlTagHandlerMapping
from inscriptis.model.html_document_state import HtmlDocumentState

from lxml.html import tostring

from haruka_parser.latex_processing import (
    extract_math,
    extract_delimited_math,
    get_math_config,
    latex_regex,
)
from haruka_parser.tree_processing import (
    fix_encode_html,
    remove_jax_ignore,
    remove_buttons,
    remove_image_figures,
    extract_code,
    extract_tables,
    extract_headings,
    remove_dense_links,
    add_se_separators,
    wikipedia_preprocess,
    remove_display_none,
    remove_svg,
    main_content_preprocess,
    post_process_headings,
    get_title,
    get_lxml_tree,
    extract_time,
)
from haruka_parser.line_processing import (
    remove_empty_headers,
    remove_edit_buttons,
    remove_chinese_characters,
    remove_boilerplate,
    restore_replacements,
)
from haruka_parser.utils import IMG_SRC_ATTR, ReplacementManager, fast_html2text
from haruka_parser.meta_processing import extract_metadata
from haruka_parser.tree_cleaning import OVERALL_DISCARD_XPATH, PAYWALL_DISCARD_XPATH, TEASER_DISCARD_XPATH, prune_unwanted_nodes, tree_cleaning, delete_by_link_density

DEFAULT_CONFIG = defaultdict(
    bool,
    {
        "add_title": True,
        "readability": False,
        "skip_large_links": False,
        "extract_image_and_link": False,
        "extract_latex": True,
        "extract_cnki_latex": False,
        "escape_dollars": True,
        "remove_buttons": True,
        "remove_edit_buttons": True,
        "remove_image_figures": False,
        "markdown_code": False,
        "markdown_headings": True,
        "remove_chinese": False,
        "boilerplate_config": {
            "enable": False,
            "ratio_threshold": 0.18,
            "absolute_threshold": 10,
            "end_threshold": 15,
        },
    },
)

selectors_path = os.path.join(
    os.path.dirname(__file__), "dictionary/banned_selectors.txt"
)
with open(selectors_path, "r") as f:
    selectors = [line.replace("\n", "").strip() for line in f]
    # Remove empty lines
    selectors = [line for line in selectors if line]

def filter_tree(tree, config, info):
    """Filters the HTML tree to remove unwanted elements."""

    # Remove display none elements
    remove_display_none(tree)

    # svg make resiliparse crack
    remove_svg(tree)

    # Remove the wikipedia footer
    wikipedia_preprocess(tree)

    if config["remove_buttons"]:
        # Remove any bootstrap buttons
        remove_buttons(tree)

    if config["remove_image_figures"]:
        # Remove any figures that only contain images
        remove_image_figures(tree)

    if config["extract_latex"]:
        remove_jax_ignore(tree)

    # Remove link lists
    remove_dense_links(tree)

    # Process stack exchange separators
    add_se_separators(tree)

    # Preprocess main content
    main_content_preprocess(tree)


def extract_tree(tree, replacement_manager, config, info):

    # Wrap the code in markdown code blocks
    info = extract_code(tree, replacement_manager, info, config["markdown_code"])

    # Record the location of headings and format them
    extract_headings(tree, replacement_manager, config["markdown_headings"])

    # Format tables
    extract_tables(tree.document, replacement_manager, config, info)


def replace_tags(html, old, new):
    pattern = re.compile(old, re.IGNORECASE)
    return pattern.sub(new, html)


def html_preprocessing(html, config):
    if config["extract_cnki_latex"]:
        # Replace consecutive subscript tags
        html = re.sub(r"_(.*?)_", r"\1", html)
        # Replace italic tags
        html = re.sub(r"<i>(.*?)</i>", r"\1", html)
        # latex_str = re.sub(r"<i>(.*?)</i>", r"$\1$", latex_str)

        html = re.sub(
            r"(<sub>(.*?)</sub>)+",
            # lambda m: "_{" + "".join(re.findall(r"<sub>(.*?)</sub>", m.group(0))) + "}",
            lambda m: "[extract_itex]"
            + "_{"
            + "".join(re.findall(r"<sub>(.*?)</sub>", m.group(0)))
            + "}"
            + "[/extract_itex]",
            html,
        )
        html = re.sub(
            r"(<sup>(.*?)</sup>)+",
            lambda m: "[extract_itex]"
            + "^{"
            + "".join(re.findall(r"<sup>(.*?)</sup>", m.group(0)))
            + "}"
            + "[/extract_itex]",
            html,
        )
    
    # Learn from obelics
    # html = re.sub(r"[ ]{2,}", " ", html)
    # html = re.sub(r"<!--(?s).*?-->", "", html)
    html = re.sub("<br>|<br/>|<br />|</br>", "[br_tag]", html)

    html = replace_tags(html, "<template", "<div")
    html = replace_tags(html, "</template", "</div")
    html = replace_tags(html, "<frameset", "<div")
    html = replace_tags(html, "</frameset>", "</div>")
    html = html.replace("&lt;math&gt;", "[itex]")
    html = html.replace("&lt;/math&gt;", "[/itex]")
    html = html.replace("$", "[extract_single_dollar]")
    html = html.replace("§", "[extract_single_chapter]")
    return html


def extract_image_and_link(tree, info):
    
    image_dict = {}
    link_list = []  
    img_nodes = tree.document.query_selector_all("img")
    # no, this is not normally used alone without <img> nearby
    # img_nodes += list(tree.document.query_selector_all("source"))
    link_nodes = tree.document.query_selector_all("a")
    
    for idx, img_node in enumerate(img_nodes):
        img_attrs = {name: img_node.getattr(name) for name in img_node.attrs}
        for source_type in IMG_SRC_ATTR:
            img_src = img_attrs.pop(source_type, None)
            if img_src:
                break
        img_caption = img_attrs.pop("alt", None)
        if img_src:
            image_dict[str(idx)] = {"caption": img_caption, "url": img_src, "meta": img_attrs}
            # Make a new p tag
            new_p = tree.create_element("span")
            new_p.html = f"[extract_image_tag_{idx}]"
            img_node.parent.replace_child(new_p, img_node)
        else:
            img_node.parent.remove_child(img_node)
    
    for link_node in link_nodes:
        link_src = link_node.getattr('href')
        if link_src:
            link_list.append(link_src)
    
    info['image_dict'] = image_dict
    info['links'] = link_list

def divide_text_into_list(text, info):
    # 使用正则表达式来匹配形如 [extract_image_tag_{数字}] 的标记
    pattern = r'\[extract_image_tag_\d+\]'
    number_pattern = r'\[extract_image_tag_(\d+)\]'
    
    # 分割文本，保留标记作为分割结果的一部分
    text_parts = re.split(f'({pattern})', text)

    # 初始化一个列表来保存处理后的文本和None（对应标记的位置）
    processed_text = []
    images = []
    image_dict = info.pop('image_dict', {})
    new_image_list = []
    
    for part in text_parts:
        # 检查当前部分是否匹配我们的标记模式
        match = re.match(number_pattern, part)
        if match:
            # 如果是标记，根据标记中的索引从info中获取对应的图片URL
            img_idx = match.group(1)  # 提取标记中的数字索引
            # 从info字典的'image_dict'中获取对应索引的图片URL，注意索引可能需要调整
            img_url = image_dict[img_idx]['url']
            # 在对应的位置添加None到文本列表，并将图片URL添加到图片列表
            processed_text.append(None)
            images.append(img_url)
            new_image_list.append(image_dict[img_idx])
        else:
            # 如果不是标记，则直接添加文本部分到列表，并在图片列表中添加None
            processed_text.append(part)
            images.append(None)
    
    info["text_list"] = processed_text
    info["images"] = images
    info['images_meta'] = new_image_list
    # 返回处理后的文本和图片URL列表
    return info


def extract_text(html, config=DEFAULT_CONFIG, encoding="utf-8"):
    """Extracts plain text from an HTML string."""
    
    def _start_li(state: HtmlDocumentState, _: Dict) -> None:
        """Handle the <li> tag."""
        pass

    info = {
        "found_math": False,
        "found_latex_text": False,
        "found_latex_script": False,
        "use_readability": False,
        "script_math_tex": 0,
        "script_math_asciimath": 0,
        "math_annotations": 0,
        "math_alttext": 0,
        "mathml": 0,
        "mathjax_tag": 0,
        "mathjax_inline_tex": 0,
        "mathjax_display_tex": 0,
        "mathjax_asciimath": 0,
        "img_math": 0,
        "codecogs_latex": 0,
        "wp_latex": 0,
        "mimetex.cgi": 0,
        "/images/math/codecogs": 0,
        "mathtex.cgi": 0,
        "other_latex_img": 0,
        "katex": 0,
        "math-container": 0,
        "wp-katex-eq": 0,
        "align": 0,
        "equation": 0,
        "x-ck12": 0,
        "texerror": 0,
        "code_block": 0,
        "table": 0,
        "chinese_table": 0,
        "title": "",
        "time": "",
        "encode_type": encoding,
        "meta": {}
    }

    if not html:
        return "", info
    # NFKC normalization
    if isinstance(html, str):
        html = ftfy.fix_text(html)
    elif isinstance(html, bytes):
        html, encode_type = fix_encode_html(html, encoding)
        info["encode_type"] = encode_type
    else:
        raise TypeError("html must be str or bytes")
    
    if not html:
        return "", info

    html = unicodedata.normalize('NFKC', html)

    # because this may cause segmentation fault
    pre_process_resiliparse_tree = HTMLTree.parse(html)

    # TODO: Using the same tree parser
    try: info["title"] = get_title(pre_process_resiliparse_tree)
    except: pass

    filter_tree(pre_process_resiliparse_tree, config, info)

    pre_process_tree = get_lxml_tree(str(pre_process_resiliparse_tree))

    # try: info["time"] = extract_time(html, pre_process_tree)
    # except: pass
    try: info['meta'] = extract_metadata(pre_process_tree)
    except: pass

    # jobs done by trafilatura
    try:
        pre_process_tree = tree_cleaning(pre_process_tree)
        pre_process_tree = prune_unwanted_nodes(pre_process_tree, OVERALL_DISCARD_XPATH, with_backup=True)
        pre_process_tree = prune_unwanted_nodes(pre_process_tree, PAYWALL_DISCARD_XPATH)
        pre_process_tree = prune_unwanted_nodes(pre_process_tree, TEASER_DISCARD_XPATH)
        # remove elements by link density
        pre_process_tree = delete_by_link_density(pre_process_tree, 'div', backtracking=True, favor_precision=False)
        pre_process_tree = delete_by_link_density(pre_process_tree, 'list', backtracking=False, favor_precision=False)
        pre_process_tree = delete_by_link_density(pre_process_tree, 'p', backtracking=False, favor_precision=False)
    except:
        pass
    
    full_html = get_html(pre_process_tree)
        
    if config["readability"]:
        try:
            
            full_content = fast_html2text(full_html, filter_length = 20)
            # origin readability
            html, clean_tree = Document(pre_process_tree).summary()

            clean_content = fast_html2text(html, filter_length = 20)

            if (len(clean_content) + 200) / (len(full_content) + 200) < 0.67:
                html = full_html
            else:
                info["use_readability"] = True
        except:
            html = full_html
    else:
        html = full_html

    html = html_preprocessing(html, config)
    tree = HTMLTree.parse(html)
    replacement_manager = ReplacementManager()

    if config["skip_large_links"]:
        links = tree.document.query_selector_all("a")
        span_links = tree.document.query_selector_all("span a")
        if len(links) > 3000 or len(span_links) > 3000:
            print("Too many links, skipping")
            return None, None

    if config["extract_latex"]:
        # 2 usage of math_config, for katex parsing and check if possible math exists
        if latex_regex.search(tree.document.html):
            info["found_latex_text"] = True
        math_config = get_math_config(tree.document.html)
        if math_config is not None:
            info["found_latex_script"] = True
        extract_math(tree, replacement_manager, info)
    if config["extract_image_and_link"]:
        extract_image_and_link(tree, info)
    try: extract_tree(tree, replacement_manager, config, info)
    except: pass

    lxml_tree = get_lxml_tree(str(tree))
    if lxml_tree is not None:
        # info["title"] = info["title"] or restore_replacements(
        #     get_title(lxml_tree), replacement_manager, config
        # )
        parser_config = ParserConfig(
            css=CSS_PROFILES["strict"], 
            display_images=False,
            custom_html_tag_handler_mapping=CustomHtmlTagHandlerMapping(
                start_tag_mapping={
                    "li": _start_li,
                },
                end_tag_mapping={}
            )
        )
        text = Inscriptis(
            lxml_tree,
            parser_config,
        ).get_text()
        info["html_parser"] = "inscriptis"
    else:
        # Disable their filters because we use our own.
        text = extract_plain_text(
            tree, main_content=True, alt_texts=False, skip_elements=selectors
        )
        info["html_parser"] = "resiliparse"

    if config["extract_latex"]:
        text = extract_delimited_math(text, math_config, info, replacement_manager)

    text = post_process_headings(text)

    lines = text.split("\n")

    if config["remove_chinese"]:
        # Remove Chinese characters
        lines = remove_chinese_characters(lines)

    if config["boilerplate_config"]["enable"]:
        # Remove boilerplate
        lines = remove_boilerplate(
            lines, config["boilerplate_config"], replacement_manager
        )

    # Remove headings with nothing (or only other headings) after
    lines = remove_empty_headers(lines, replacement_manager)

    # Strip lines
    lines = [line.rstrip() for line in lines]

    # Create the final string
    text = "\n".join(lines)

    if config["remove_edit_buttons"]:
        # Remove edit buttons
        lines = text.split("\n")
        lines = remove_edit_buttons(lines)
        text = "\n".join(lines)

    text = restore_replacements(text, replacement_manager, config, info)
    # If there are over two newlines in a row, replace with two
    text = re.sub(r"\n{3,}", "\n\n", text)

    text = text.strip()

    if config["add_title"] and info["title"]:
        if info["title"] not in "\n".join(text.split("\n")[:3]):
            if config["markdown_headings"]:
                text = "# " + info["title"] + "\n\n" + text
            else:
                text = info["title"] + "\n\n" + text
                
    images = []
    if config["extract_image_and_link"]:
        info = divide_text_into_list(text, info)
        text = "".join([i for i in info["text_list"] if i])
        
    return text, info
