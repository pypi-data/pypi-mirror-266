def _drop_duplicates(
    elems: List[Union[_TableHeader, _TableRow]], threshold: float
) -> List[Union[_TableHeader, _TableRow]]:
    if not 0 < threshold <= 1:
        raise ValueError("Threshold must be a number between 0 and 1")

    filtered_elems = []
    for i, elem1 in enumerate(elems):
        has_overlap = False
        for j, elem2 in enumerate(elems):
            if i == j:
                continue  # Don't compare with itself

            overlap = _calc_bbox_intersection(elem1.bbox, elem2.bbox)
            if not overlap:
                overlap_area = 0.0
            else:
                overlap_area = (overlap[2] - overlap[0]) * (overlap[3] - overlap[1])
            elem1_area = _calc_area(elem1.bbox)
            elem2_area = _calc_area(elem2.bbox)

            if overlap_area / min(elem1_area, elem2_area) > threshold:
                has_overlap = True
                # Retain the smaller element (assuming duplicates are larger)
                if elem1_area > elem2_area:
                    break

        if not has_overlap:
            filtered_elems.append(elem1)

    return filtered_elems


def _is_overlapping_with_headers(
    cell_bbox: BBox, headers: List[_TableHeader], overlap_threshold: float = 0.3
) -> bool:
    """
    Check if a given cell's bounding box overlaps with any of the header cells' bounding boxes.
    If the overlap area is above the threshold percentage of the cell's area, return True.
    """
    cell_area = calculate_area(cell_bbox)

    for header in headers:
        for hcell in header.cells:
            intersection = _calc_bbox_intersection(cell_bbox, hcell.bbox)
            if intersection:
                intersection_area = calculate_area(intersection)
                overlap_percentage = intersection_area / cell_area
                if overlap_percentage > overlap_threshold:
                    print("DROPPING")
                    return True
    return False


parser = DocumentParser(
    table_args={
        "parse": True,
        "args": {
            "parsing_algorithm": "lattice",
            "min_table_confidence": 0.75,
            "min_cell_confidence": 0.95,
            "table_output_format": "markdown",
        },
    },
)

parsed = parser.parse("path/to/sample.pdf")


def draw_prev_next_sim_bboxes(
    file: Union[str, Path, fitz.Document],
    elements: List[PrevNodeSimilarity],
) -> fitz.Document:
    pdf = load_doc(file)

    for page in pdf:
        page.wrap_contents()

        for node_info in elements:
            node = node_info["node"]
            prev_similarity = node_info.get("prev_similarity", 0.0)

            if node.bbox[0].page != page.number:
                continue

            r = fitz.Rect(
                node.bbox[0].x0, node.bbox[0].y0, node.bbox[0].x1, node.bbox[0].y1
            )

            color = (random.random(), random.random(), random.random())

            page.draw_rect(r, color, width=1.5)

            if not prev_similarity:
                continue
            sim_text = f"Prev Sim: {prev_similarity:.2f}"
            page.insert_text(
                (node.bbox[0].x0, node.bbox[0].y0), sim_text, fontsize=11, color=color
            )

    return pdf

    # def add_rect_annotation(
    #     self,
    #     page_number: int,
    #     rect: tuple[float, float, float, float],
    # ) -> None:
    #     """
    #     Adds a rectangle annotation to a specific page.

    #     Args:
    #         page_number (int): The page number (0-indexed) to add the annotation to.
    #         rect (tuple): A tuple of the form (x0, y0, x1, y1) specifying the rectangle's position.
    #         color (tuple): A tuple specifying the color of the rectangle in RGB, default is red.
    #         stroke_width (int): The width of the stroke line for the rectangle.
    #     """
    #     rect_obj = Rectangle(rect=rect)

    #     if page_number >= len(self.reader.pages):
    #         raise ValueError(f"Page number {page_number} out of range.")
    #     else:
    #         self.writer.add_annotation(page_number=page_number, annotation=rect_obj)


from typing import Union, List, Sequence, Optional

from openparse.schemas import Node, PrevNodeSimilarity
from openparse.pdf import Pdf


def draw_bboxes(
    doc: Pdf,
    nodes: list[Node],
    draw_sub_elements: bool = False,
) -> Pdf:
    if draw_sub_elements:
        raise NotImplementedError("Sub-elements are not yet supported.")

    flattened_bboxes = [bbox for node in nodes for bbox in node.bbox]

    for bbox in flattened_bboxes:
        doc.add_rect_annotation(
            page_number=bbox.page,
            rect=(bbox.x0, bbox.y0, bbox.x1, bbox.y1),
        )
    return doc


def display_doc(
    doc: Pdf,
    page_nums: Optional[list[int]] = None,
) -> None:
    """
    Display a single page of a PDF file using IPython.
    """
    try:
        from IPython.display import Image, display  # type: ignore
    except ImportError:
        raise ImportError(
            "IPython is required to display PDFs. Please install it with `pip install ipython`."
        )

    pdoc = doc.to_pymupdf_doc()
    if not page_nums:
        page_nums = list(range(pdoc.page_count))
    for page_num in page_nums:
        page = pdoc[page_num]
        img_data = page.get_pixmap().tobytes("png")
        display(Image(data=img_data))

TABLE bbox=(35.36741638183594, 96.37252807617188, 691.6922607421875, 517.9938354492188) headers=[_TableHeader(cells=[_TableHeaderCell(bbox=(206.15311362526631, 105.64504189924759, 361.92600180886006, 123.22541184858841), content=None, variant='header'), _TableHeaderCell(bbox=(521.5474922873757, 105.70714898542923, 690.0865547873757, 123.22541184858841), content=None, variant='header'), _TableHeaderCell(bbox=(360.2500069358132, 105.74062486128372, 410.5702278830788, 123.22541184858841), content=None, variant='header'), _TableHeaderCell(bbox=(411.57538535378194, 105.81761880354446, 452.10687949440694, 123.22541184858841), content=None, variant='header'), _TableHeaderCell(bbox=(452.4295723655007, 105.89149613813919, 497.28964926979756, 123.22541184858841), content=None, variant='header'), _TableHeaderCell(bbox=(35.182784340598346, 105.96672578291458, 206.06037070534444, 123.22541184858841), content=None, variant='header'), _TableHeaderCell(bbox=(496.0791084983132, 105.98925919966263, 521.5678169944069, 123.22541184858841), content=None, variant='header')])] rows=[_TableRow(cells=[_TableDataCell(bbox=(35.22977759621358, 123.52590699629349, 206.06037070534444, 143.69812150435013), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 123.52590699629349, 361.92600180886006, 143.69812150435013), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 123.52590699629349, 410.5702278830788, 143.69812150435013), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 123.52590699629349, 452.10687949440694, 143.69812150435013), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 123.52590699629349, 497.28964926979756, 143.69812150435013), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 123.52590699629349, 521.5678169944069, 143.69812150435013), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 123.52590699629349, 690.0865547873757, 143.69812150435013), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 130.52832932905716, 206.06037070534444, 516.4211592240767), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 130.52832932905716, 209.55084922096944, 516.4211592240767), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.20100333473897, 143.6793379350142, 206.06037070534444, 160.27500291304153), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 143.6793379350142, 361.92600180886006, 160.27500291304153), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 143.6793379350142, 410.5702278830788, 160.27500291304153), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 143.6793379350142, 452.10687949440694, 160.27500291304153), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 143.6793379350142, 497.28964926979756, 160.27500291304153), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 143.6793379350142, 521.5678169944069, 160.27500291304153), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 143.6793379350142, 690.0865547873757, 160.27500291304153), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.129248879172565, 160.296967939897, 206.06037070534444, 176.68047471479935), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 160.296967939897, 361.92600180886006, 176.68047471479935), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 160.296967939897, 410.5702278830788, 176.68047471479935), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 160.296967939897, 452.10687949440694, 176.68047471479935), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 160.296967939897, 497.28964926979756, 176.68047471479935), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 160.296967939897, 521.5678169944069, 176.68047471479935), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 160.296967939897, 690.0865547873757, 176.68047471479935), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 176.78753800825638, 206.06037070534444, 193.39771409468216), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 176.78753800825638, 361.92600180886006, 193.39771409468216), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 176.78753800825638, 410.5702278830788, 193.39771409468216), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 176.78753800825638, 452.10687949440694, 193.39771409468216), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 176.78753800825638, 497.28964926979756, 193.39771409468216), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 176.78753800825638, 521.5678169944069, 193.39771409468216), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 176.78753800825638, 690.0865547873757, 193.39771409468216), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 193.34961076216263, 206.06037070534444, 209.94493241743606), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 193.34961076216263, 361.92600180886006, 209.94493241743606), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 193.34961076216263, 410.5702278830788, 209.94493241743606), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 193.34961076216263, 452.10687949440694, 209.94493241743606), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 193.34961076216263, 497.28964926979756, 209.94493241743606), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 193.34961076216263, 521.5678169944069, 209.94493241743606), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 193.34961076216263, 690.0865547873757, 209.94493241743606), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 209.7849287553267, 206.06037070534444, 226.38141007856888), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 209.7849287553267, 361.92600180886006, 226.38141007856888), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 209.7849287553267, 410.5702278830788, 226.38141007856888), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 209.7849287553267, 452.10687949440694, 226.38141007856888), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 209.7849287553267, 497.28964926979756, 226.38141007856888), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 209.7849287553267, 521.5678169944069, 226.38141007856888), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 209.7849287553267, 690.0865547873757, 226.38141007856888), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 226.48010392622513, 206.06037070534444, 242.9812483354048), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 226.48010392622513, 361.92600180886006, 242.9812483354048), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 226.48010392622513, 410.5702278830788, 242.9812483354048), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 226.48010392622513, 452.10687949440694, 242.9812483354048), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 226.48010392622513, 497.28964926979756, 242.9812483354048), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 226.48010392622513, 521.5678169944069, 242.9812483354048), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 226.48010392622513, 690.0865547873757, 242.9812483354048), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 243.06179948286575, 206.06037070534444, 259.6156630082564), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 243.06179948286575, 361.92600180886006, 259.6156630082564), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 243.06179948286575, 410.5702278830788, 259.6156630082564), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 243.06179948286575, 452.10687949440694, 259.6156630082564), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 243.06179948286575, 497.28964926979756, 259.6156630082564), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 243.06179948286575, 521.5678169944069, 259.6156630082564), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 243.06179948286575, 690.0865547873757, 259.6156630082564), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 259.36580033735794, 206.06037070534444, 275.8905958695845), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 259.36580033735794, 361.92600180886006, 275.8905958695845), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 259.36580033735794, 410.5702278830788, 275.8905958695845), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 259.36580033735794, 452.10687949440694, 275.8905958695845), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 259.36580033735794, 497.28964926979756, 275.8905958695845), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 259.36580033735794, 521.5678169944069, 275.8905958695845), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 259.36580033735794, 690.0865547873757, 275.8905958695845), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.13444068215108, 276.3870100541548, 206.06037070534444, 292.8090986772017), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 276.3870100541548, 361.92600180886006, 292.8090986772017), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 276.3870100541548, 410.5702278830788, 292.8090986772017), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 276.3870100541548, 452.10687949440694, 292.8090986772017), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 276.3870100541548, 497.28964926979756, 292.8090986772017), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 276.3870100541548, 521.5678169944069, 292.8090986772017), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 276.3870100541548, 690.0095894553444, 292.8090986772017), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.13354041359639, 292.3361525102095, 206.06037070534444, 308.8550428910689), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 292.3361525102095, 361.92600180886006, 308.8550428910689), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 292.3361525102095, 410.5702278830788, 308.8550428910689), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 292.3361525102095, 452.10687949440694, 308.8550428910689), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 292.3361525102095, 497.28964926979756, 308.8550428910689), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 292.3361525102095, 521.5678169944069, 308.8550428910689), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 292.3361525102095, 690.0865547873757, 308.8550428910689), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 308.5428633256392, 206.06037070534444, 325.1110243363814), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 308.5428633256392, 361.92600180886006, 325.1110243363814), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 308.5428633256392, 410.5702278830788, 325.1110243363814), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 308.5428633256392, 452.10687949440694, 325.1110243363814), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 308.5428633256392, 497.28964926979756, 325.1110243363814), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 308.5428633256392, 521.5678169944069, 325.1110243363814), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 308.5428633256392, 690.0865547873757, 325.1110243363814), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.216128609397174, 325.67996354536575, 206.06037070534444, 342.2242598100142), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 325.67996354536575, 361.92600180886006, 342.2242598100142), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 325.67996354536575, 410.5702278830788, 342.2242598100142), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 325.67996354536575, 452.10687949440694, 342.2242598100142), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 325.67996354536575, 497.28964926979756, 342.2242598100142), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 325.67996354536575, 521.5678169944069, 342.2242598100142), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 325.67996354536575, 690.0865547873757, 342.2242598100142), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 341.9986738725142, 206.06037070534444, 358.4926008744673), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 341.9986738725142, 361.92600180886006, 358.4926008744673), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 341.9986738725142, 410.5702278830788, 358.4926008744673), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 341.9986738725142, 452.10687949440694, 358.4926008744673), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 341.9986738725142, 497.28964926979756, 358.4926008744673), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 341.9986738725142, 521.5678169944069, 358.4926008744673), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 341.9986738725142, 690.0865547873757, 358.4926008744673), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 358.5333418412642, 206.06037070534444, 375.10054154829544), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 358.5333418412642, 361.92600180886006, 375.10054154829544), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 358.5333418412642, 410.5702278830788, 375.10054154829544), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 358.5333418412642, 452.10687949440694, 375.10054154829544), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 358.5333418412642, 497.28964926979756, 375.10054154829544), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 358.5333418412642, 521.5678169944069, 375.10054154829544), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 358.5333418412642, 690.0865547873757, 375.10054154829544), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.17559745094991, 375.1639875932173, 206.06037070534444, 391.70527787642044), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 375.1639875932173, 361.92600180886006, 391.70527787642044), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 375.1639875932173, 410.5702278830788, 391.70527787642044), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 375.1639875932173, 452.10687949440694, 391.70527787642044), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 375.1639875932173, 497.28964926979756, 391.70527787642044), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 375.1639875932173, 521.5678169944069, 391.70527787642044), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 375.1639875932173, 690.0448677756569, 391.70527787642044), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.18905188820577, 391.7489180131392, 206.06037070534444, 408.2126936479048), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 391.7489180131392, 361.92600180886006, 408.2126936479048), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 391.7489180131392, 410.5702278830788, 408.2126936479048), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 391.7489180131392, 452.10687949440694, 408.2126936479048), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 391.7489180131392, 497.28964926979756, 408.2126936479048), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 391.7489180131392, 521.5678169944069, 408.2126936479048), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 391.7489180131392, 690.0088570334694, 408.2126936479048), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.288272164084674, 408.22346635298294, 206.06037070534444, 424.6131758256392), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 408.22346635298294, 361.92600180886006, 424.6131758256392), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 408.22346635298294, 410.5702278830788, 424.6131758256392), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 408.22346635298294, 452.10687949440694, 424.6131758256392), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 408.22346635298294, 497.28964926979756, 424.6131758256392), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 408.22346635298294, 521.5678169944069, 424.6131758256392), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 408.22346635298294, 690.0443794944069, 424.6131758256392), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.265181801535846, 424.74266190962356, 206.06037070534444, 441.19603105024856), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 424.74266190962356, 361.92600180886006, 441.19603105024856), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 424.74266190962356, 410.5702278830788, 441.19603105024856), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 424.74266190962356, 452.10687949440694, 441.19603105024856), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 424.74266190962356, 497.28964926979756, 441.19603105024856), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 424.74266190962356, 521.5678169944069, 441.19603105024856), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 424.74266190962356, 690.0817940451882, 441.19603105024856), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.130687020041705, 441.1501936479048, 206.06037070534444, 457.64375443892044), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 441.1501936479048, 361.92600180886006, 457.64375443892044), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 441.1501936479048, 410.5702278830788, 457.64375443892044), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 441.1501936479048, 452.10687949440694, 457.64375443892044), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 441.1501936479048, 497.28964926979756, 457.64375443892044), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 441.1501936479048, 521.5678169944069, 457.64375443892044), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 441.1501936479048, 690.0865547873757, 457.64375443892044), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.26417472145772, 457.65477128462356, 206.06037070534444, 474.10359330610794), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 457.65477128462356, 361.92600180886006, 474.10359330610794), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 457.65477128462356, 410.5702278830788, 474.10359330610794), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 457.65477128462356, 452.10687949440694, 474.10359330610794), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 457.65477128462356, 497.28964926979756, 474.10359330610794), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 457.65477128462356, 521.5678169944069, 474.10359330610794), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 457.65477128462356, 690.0865547873757, 474.10359330610794), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.12911917946553, 474.03270097212356, 206.06037070534444, 490.56614823774856), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 474.03270097212356, 361.92600180886006, 490.56614823774856), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 474.03270097212356, 410.5702278830788, 490.56614823774856), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 474.03270097212356, 452.10687949440694, 490.56614823774856), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 474.03270097212356, 497.28964926979756, 490.56614823774856), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 474.03270097212356, 521.5678169944069, 490.56614823774856), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 474.03270097212356, 690.0865547873757, 490.56614823774856), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.15542533180928, 490.4657454057173, 206.06037070534444, 506.47007890181106), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 490.4657454057173, 361.92600180886006, 506.47007890181106), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 490.4657454057173, 410.5702278830788, 506.47007890181106), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 490.4657454057173, 452.10687949440694, 506.47007890181106), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 490.4657454057173, 497.28964926979756, 506.47007890181106), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 490.4657454057173, 521.5678169944069, 506.47007890181106), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 490.4657454057173, 690.0865547873757, 506.47007890181106), content=None, variant='data')]), _TableRow(cells=[_TableDataCell(bbox=(35.117327950217486, 506.24861283735794, 206.06037070534444, 519.2454695268111), content=None, variant='data'), _TableDataCell(bbox=(206.15311362526631, 506.24861283735794, 361.92600180886006, 519.2454695268111), content=None, variant='data'), _TableDataCell(bbox=(360.2500069358132, 506.24861283735794, 410.5702278830788, 519.2454695268111), content=None, variant='data'), _TableDataCell(bbox=(411.57538535378194, 506.24861283735794, 452.10687949440694, 519.2454695268111), content=None, variant='data'), _TableDataCell(bbox=(452.4295723655007, 506.24861283735794, 497.28964926979756, 519.2454695268111), content=None, variant='data'), _TableDataCell(bbox=(496.0791084983132, 506.24861283735794, 521.5678169944069, 519.2454695268111), content=None, variant='data'), _TableDataCell(bbox=(521.5474922873757, 506.24861283735794, 690.0865547873757, 519.2454695268111), content=None, variant='data')])] 7
