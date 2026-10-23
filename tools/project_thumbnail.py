"""Keep the native project's stored previews aligned with its reviewed cover."""

from base64 import b64encode
from io import BytesIO

from lxml import etree
from PIL import Image

from release_support import digest, source_path


THUMBNAIL_MEMBERS = frozenset({"screenshot.png", "content/resources/screenshot.png"})
NS = {"o": "http://www.intef.es/xsd/ode"}


def load_project_thumbnail(root, version):
    specification = version.get("elpx_thumbnail")
    if not isinstance(specification, dict) or not {"path", "sha256", "width", "height"} <= specification.keys():
        raise ValueError("Missing current ELPX thumbnail metadata")
    dimensions = (specification["width"], specification["height"])
    if any(type(value) is not int or value <= 0 for value in dimensions):
        raise ValueError("Invalid ELPX thumbnail dimensions")
    payload = source_path(root, specification["path"]).read_bytes()
    if digest(payload) != specification["sha256"]:
        raise ValueError("ELPX thumbnail checksum does not match its reviewed image")
    try:
        with Image.open(BytesIO(payload)) as image:
            if image.format != "PNG":
                raise ValueError("Unexpected image format")
            actual_dimensions = image.size
            image.verify()
    except (OSError, SyntaxError, ValueError) as error:
        raise ValueError("ELPX thumbnail must be a valid PNG") from error
    if actual_dimensions != dimensions:
        raise ValueError("ELPX thumbnail dimensions do not match its metadata")
    return payload


def thumbnail_data_uri(payload):
    return "data:image/png;base64," + b64encode(payload).decode("ascii")


def verify_project_thumbnail(files):
    payload = files.get("screenshot.png")
    if not payload or any(files.get(name) != payload for name in THUMBNAIL_MEMBERS):
        raise ValueError("The project thumbnail copies are missing or inconsistent")
    tree = etree.fromstring(files["content.xml"], etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True))
    values = tree.findall(".//o:odeProperty[o:key='pp_screenshot']/o:value", NS)
    if len(values) != 1 or values[0].text != thumbnail_data_uri(payload):
        raise ValueError("The project thumbnail differs from its editor preview metadata")
