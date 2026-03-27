import xml.etree.ElementTree as ET

def parse_phyphox(file_path):
    """Abre el archivo físico y extrae los contenedores de datos."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = {}
    for c in root.findall('.//container'):
        if c.text and c.get('init'):
            # Limpiamos los NaNs para proteger los cálculos posteriores
            data[c.text] = [float(x) if x.strip().lower() != 'nan' else 0.0 
                            for x in c.get('init').split(',') if x.strip()]
    return data