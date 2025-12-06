def get_input_fields(self, input_name: str) -> dict:
    """
    Returns all text and image fields for a given input.
    {
        "texts": [...],
        "images": [...]
    }
    """
    xml = self.get_status_xml()
    data = self.parse_xml(xml)

    # find input
    for inp in data.get("inputs", []):
        if inp["title"].lower() == input_name.lower():
            fields = {"texts": [], "images": []}
            for f in inp.get("text", []):
                fields["texts"].append(f["name"])
            for f in inp.get("images", []):
                fields["images"].append(f["name"])
            return fields

    raise ValueError(f"Input not found: {input_name}")
