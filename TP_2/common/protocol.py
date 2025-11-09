import struct

# El tamaño de la longitud del mensaje (4 bytes, unsigned int)
HEADER_SIZE = 4

def encode_message(data: dict) -> bytes:
    """Codifica datos en el formato: | longitud (4 bytes) | datos serializados |"""
    from .serialization import serialize_data
    
    serialized = serialize_data(data)
    # Empaqueta la longitud como un entero de 4 bytes (little-endian)
    header = struct.pack('<I', len(serialized)) 
    return header + serialized

def decode_header(header_bytes: bytes) -> int:
    """Decodifica la longitud del mensaje del encabezado de 4 bytes."""
    # Desempaqueta un entero de 4 bytes (little-endian)
    return struct.unpack('<I', header_bytes)[0]