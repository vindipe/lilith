import lxml.etree as ET

def remove_tags_with_primary_secondary(root):
    tags_to_remove = ['service', 'bridge', 'link', 'schedule']
    for tag in tags_to_remove:
        for elem in root.iter(tag):
            for attr_key, attr_value in elem.attrib.items():
                if "primary" in attr_value or "secondary" in attr_value:
                    parent = elem.getparent()
                    parent.remove(elem)
                    break

def main():
    tree = ET.parse('kollaps/examples/topology.xml')    
    root = tree.getroot()

    remove_tags_with_primary_secondary(root)

    tree.write('kollaps/examples/topology.xml')

if __name__ == "__main__":
    main()