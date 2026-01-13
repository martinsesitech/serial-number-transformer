import hashlib
import base64
import math

class SerialTransformer:
    """
    Transforms serial numbers between original format and public 8-char codes.
    
    Original format: YYBB-PMMM-6NNN
    Public format: 8-character uppercase alphanumeric (Base36)
    
    Product Types:
    1 = GrainMate
    2 = FarmSense
    """
    
    def __init__(self):
        # Configuration
        self.PRIME = 1000000007  # Large prime number
        self.MODULUS = 36**8     # 36^8 = 2,821,109,907,456
        self.BASE36_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        # Product definitions
        self.PRODUCTS = {
            1: {
                "name": "GrainMate",
                "models": {
                    "101": "GM-101",
                    "102": "GM-102",
                    "103": "GM-103"
                }
            },
            2: {
                "name": "FarmSense",
                "models": {
                    "100": "FS-100"
                }
            }
        }
        
        # Pre-calculate modular inverse for faster decoding
        self.INVERSE = self._mod_inverse(self.PRIME, self.MODULUS)
    
    def _mod_inverse(self, a, m):
        """Calculate modular inverse using Extended Euclidean Algorithm"""
        def egcd(a, b):
            if b == 0:
                return a, 1, 0
            else:
                g, x, y = egcd(b, a % b)
                return g, y, x - (a // b) * y
        
        g, x, _ = egcd(a, m)
        if g != 1:
            alt_prime = 1000000009
            g, x, _ = egcd(alt_prime, m)
            if g == 1:
                self.PRIME = alt_prime
            else:
                raise ValueError("Cannot find modular inverse")
        
        return x % m

    def _serial_to_int(self, original_serial):
        """Convert YYBB-PMMM-6NNN to integer"""
        clean = original_serial.replace("-", "")
        
        if not clean.isdigit() or len(clean) != 12:
            raise ValueError(f"Invalid serial format: {original_serial}")
        
        return int(clean)
    
    def _int_to_serial(self, num):
        """Convert integer back to YYBB-PMMM-6NNN format"""
        original_str = str(num).zfill(12)
        return f"{original_str[:4]}-{original_str[4:8]}-{original_str[8:]}"
    
    def to_public(self, original_serial):
        """Convert original serial to public 8-char code"""
        serial_num = self._serial_to_int(original_serial)
        transformed = (serial_num * self.PRIME) % self.MODULUS
        
        result = ""
        temp = transformed
        for _ in range(8):
            temp, remainder = divmod(temp, 36)
            result = self.BASE36_CHARS[remainder] + result
        
        return result
    
    def to_original(self, public_code):
        """Convert public code back to original serial format"""
        if len(public_code) != 8:
            raise ValueError(f"Public code must be 8 characters, got {len(public_code)}")
        
        if not all(c in self.BASE36_CHARS for c in public_code):
            raise ValueError(f"Public code contains invalid characters")
        
        num = 0
        for char in public_code:
            num = num * 36 + self.BASE36_CHARS.index(char)
        
        original_num = (num * self.INVERSE) % self.MODULUS
        return self._int_to_serial(original_num)
    
    def parse_serial(self, original_serial):
        """Parse YYBB-PMMM-6NNN into its components"""
        if not self._is_valid_serial(original_serial):
            raise ValueError(f"Invalid serial format: {original_serial}")
        
        parts = original_serial.split("-")
        yybb = parts[0]
        pmmm = parts[1]
        snnn = parts[2]
        
        year = "20" + yybb[:2]
        batch = int(yybb[2:])
        product_type = int(pmmm[0])
        model_code = pmmm[1:]
        sequence = int(snnn[1:])
        
        # Get product and model names
        product_info = self.PRODUCTS.get(product_type, {"name": "Unknown Product"})
        product_name = product_info["name"]
        
        model_name = product_info.get("models", {}).get(model_code, f"Unknown Model {model_code}")
        
        return {
            "original": original_serial,
            "year": year,
            "batch": batch,
            "product_type": product_type,
            "product_name": product_name,
            "model_code": model_code,
            "model": model_name,
            "sequence": sequence,
            "unit_number": f"Unit {sequence:03d}"
        }
    
    def generate_batch(self, year, batch_num, product_type, model, start_unit=1, end_unit=100):
        """Generate a batch of serial numbers"""
        results = []
        
        for unit in range(start_unit, end_unit + 1):
            original = f"{year:02d}{batch_num:02d}-{product_type}{model:03d}-6{unit:03d}"
            public = self.to_public(original)
            
            results.append({
                "unit": unit,
                "original": original,
                "public": public
            })
        
        return results
    
    def get_available_products(self):
        """Return list of available products and models"""
        return self.PRODUCTS
    
    def _is_valid_serial(self, serial):
        """Validate the serial number format"""
        if not isinstance(serial, str):
            return False
        
        parts = serial.split("-")
        if len(parts) != 3:
            return False
        
        if len(parts[0]) != 4 or not parts[0].isdigit():
            return False
        
        if len(parts[1]) != 4 or not parts[1].isdigit():
            return False
        
        if len(parts[2]) != 4 or not parts[2].startswith('6') or not parts[2][1:].isdigit():
            return False
        
        # Check if product type is valid
        product_type = int(parts[1][0])
        if product_type not in self.PRODUCTS:
            return False
        
        # Check if model exists for this product
        model_code = parts[1][1:]
        if model_code not in self.PRODUCTS[product_type]["models"]:
            return False
        
        return True


def show_available_products(transformer):
    """Display available products and models"""
    print("\nAVAILABLE PRODUCTS & MODELS:")
    print("-" * 40)
    
    products = transformer.get_available_products()
    for product_code, product_info in products.items():
        print(f"\nProduct {product_code}: {product_info['name']}")
        for model_code, model_name in product_info["models"].items():
            print(f"  Model {model_code}: {model_name}")
    
    print("\nSerial Format: YYBB-PMMM-6NNN")
    print("  YY = Year (20 for 2020, 21 for 2021, etc.)")
    print("  BB = Batch number (01, 02, etc.)")
    print("  P = Product type (1=GrainMate, 2=FarmSense)")
    print("  MMM = Model code (101, 102, 100, etc.)")
    print("  6NNN = Unit number (6001 = 1st unit)")


def encode_serial_interactive():
    """Interactive serial encoding"""
    print("\n--- ENCODE A SERIAL ---\n")
    
    transformer = SerialTransformer()
    
    # Show available products
    show_available_products(transformer)
    
    while True:
        print("\nEnter a serial number in format YYBB-PMMM-6NNN")
        print("Examples: 2005-1102-6100, 2402-2100-6001")
        print("Enter 'back' to return to main menu")
        
        original = input("\nSerial: ").strip().upper()
        
        if original.lower() == 'back':
            return
        
        if original == '':
            continue
        
        try:
            # Validate and parse
            if not transformer._is_valid_serial(original):
                print("ERROR: Invalid format! Must be YYBB-PMMM-6NNN")
                print("   Check product type and model are valid")
                continue
            
            parsed = transformer.parse_serial(original)
            
            # Transform to public code
            public = transformer.to_public(original)
            
            # Show results
            print(f"\nENCODING SUCCESSFUL")
            print(f"Original Serial: {original}")
            print(f"Public Code:     {public}")
            
            print(f"\nProduct Details:")
            print(f"  Product: {parsed['product_name']}")
            print(f"  Model:   {parsed['model']}")
            print(f"  Year:    {parsed['year']}")
            print(f"  Batch:   {parsed['batch']}")
            print(f"  Unit:    {parsed['unit_number']}")
            
            # Ask if user wants to decode back
            decode = input("\nDecode this back to verify? (y/n): ").lower()
            if decode == 'y':
                decoded = transformer.to_original(public)
                if original == decoded:
                    print(f"Verification passed: {public} -> {decoded}")
                else:
                    print(f"ERROR: Verification failed!")
                    print(f"   Original: {original}")
                    print(f"   Decoded:  {decoded}")
            
        except Exception as e:
            print(f"ERROR: {e}")


def decode_serial_interactive():
    """Interactive serial decoding"""
    print("\n--- DECODE A PUBLIC CODE ---\n")
    
    transformer = SerialTransformer()
    
    while True:
        print("\nEnter an 8-character public code (0-9, A-Z)")
        print("Examples: 5LRG6030, 4NXKHLX3")
        print("Enter 'back' to return to main menu")
        
        public_code = input("\nPublic Code: ").strip().upper()
        
        if public_code.lower() == 'back':
            return
        
        if public_code == '':
            continue
        
        try:
            # Decode to original
            original = transformer.to_original(public_code)
            
            # Parse details
            parsed = transformer.parse_serial(original)
            
            # Show results
            print(f"\nDECODING SUCCESSFUL")
            print(f"Public Code:     {public_code}")
            print(f"Original Serial: {original}")
            
            print(f"\nProduct Details:")
            print(f"  Product: {parsed['product_name']}")
            print(f"  Model:   {parsed['model']}")
            print(f"  Year:    {parsed['year']}")
            print(f"  Batch:   {parsed['batch']}")
            print(f"  Unit:    {parsed['unit_number']}")
            
            # Ask if user wants to encode back
            encode = input("\nEncode this back to verify? (y/n): ").lower()
            if encode == 'y':
                re_encoded = transformer.to_public(original)
                if public_code == re_encoded:
                    print(f"Verification passed: {original} -> {re_encoded}")
                else:
                    print(f"ERROR: Verification failed!")
                    print(f"   Expected: {public_code}")
                    print(f"   Got:      {re_encoded}")
            
        except Exception as e:
            print(f"ERROR: {e}")


def batch_generation_interactive():
    """Interactive batch generation"""
    print("\n--- GENERATE A BATCH ---\n")
    
    transformer = SerialTransformer()
    
    # Show available products
    print("\nAVAILABLE PRODUCTS:")
    products = transformer.get_available_products()
    for product_code, product_info in products.items():
        print(f"  {product_code}: {product_info['name']}")
    
    try:
        print("\nEnter batch details:")
        year = int(input("Year (last 2 digits, e.g., 24 for 2024): "))
        batch_num = int(input("Batch number (e.g., 1): "))
        product_type = int(input("Product type (1=GrainMate, 2=FarmSense): "))
        
        if product_type not in products:
            print(f"ERROR: Invalid product type. Must be 1 or 2.")
            return
        
        # Show available models for selected product
        product_name = products[product_type]["name"]
        available_models = products[product_type]["models"]
        
        print(f"\nAvailable models for {product_name}:")
        for model_code, model_name in available_models.items():
            print(f"  {model_code}: {model_name}")
        
        model = input("Model code (e.g., 101, 100): ").strip()
        
        if model not in available_models:
            print(f"ERROR: Invalid model. Available models: {list(available_models.keys())}")
            return
        
        start_unit = int(input("Starting unit number (e.g., 1): "))
        end_unit = int(input("Ending unit number (e.g., 10): "))
        
        if start_unit > end_unit:
            print("ERROR: Starting unit must be less than or equal to ending unit")
            return
        
        if end_unit - start_unit > 100:
            print("WARNING: Generating more than 100 units")
            proceed = input("Continue? (y/n): ").lower()
            if proceed != 'y':
                return
        
        # Generate batch
        print(f"\nGenerating {end_unit - start_unit + 1} serials...")
        batch = transformer.generate_batch(year, batch_num, product_type, int(model), start_unit, end_unit)
        
        # Get product info for display
        product_info = products[product_type]
        model_name = product_info["models"][model]
        
        # Display results
        print(f"\nBATCH: {product_name} {model_name}")
        print(f"Batch ID: {year:02d}{batch_num:02d}")
        print(f"Units: {start_unit:03d} to {end_unit:03d}")
        
        print("\nCSV Format (copy to spreadsheet):")
        print("Unit,Original Serial,Public Code")
        for item in batch:
            print(f"{item['unit']},{item['original']},{item['public']},{item['public']}")
        
        print(f"\nSummary:")
        print(f"  Product: {product_name} {model_name}")
        print(f"  Batch: {year:02d}{batch_num:02d}")
        print(f"  Total units: {len(batch)}")
        print(f"  Range: Unit {start_unit:03d} to Unit {end_unit:03d}")
        
        # Show first and last for verification
        if len(batch) > 0:
            print(f"\nSample verification:")
            print(f"  First unit: {batch[0]['original']} -> {batch[0]['public']}")
            if len(batch) > 1:
                print(f"  Last unit:  {batch[-1]['original']} -> {batch[-1]['public']}")
            
            # Verify round-trip for first unit
            decoded = transformer.to_original(batch[0]['public'])
            if batch[0]['original'] == decoded:
                print(f"  Round-trip verified for first unit")
            else:
                print(f"  ERROR: Round-trip failed for first unit!")
        
        # Save to file option
        save = input("\nSave to file? (y/n): ").lower()
        if save == 'y':
            filename = f"{product_name}_{model_name}_batch{year:02d}{batch_num:02d}.csv"
            with open(filename, 'w') as f:
                f.write("Unit,Original Serial,Public Code,Product,Model\n")
                for item in batch:
                    f.write(f"{item['unit']},{item['original']},{item['public']},{product_name},{model_name}\n")
            print(f"Saved to {filename}")
            print(f"{filename} is in the project directory.")

            
    except ValueError as e:
        print(f"ERROR: Invalid input - Please enter valid numbers")
    except Exception as e:
        print(f"ERROR: {e}")


def main_menu():
    """Display main menu and handle user choice"""
    while True:
        print("\n")
        print("SERIAL NUMBER TRANSFORMATION SYSTEM")
        print("Transform YYBB-PMMM-6NNN serials to 8-character public codes")
        print()
        print("Products: 1=GrainMate, 2=FarmSense")
        print("Models: GM-101, GM-102, GM-103, FS-100")
        print()
        print("1. Encode a Serial (Original -> Public Code)")
        print("2. Decode a Public Code (Public Code -> Original)")
        print("3. Generate a Batch of Serials")
        print("4. Exit")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            encode_serial_interactive()
        elif choice == '2':
            decode_serial_interactive()
        elif choice == '3':
            batch_generation_interactive()
        elif choice == '4':
            print("Exited!")
            break
        else:
            print("\nERROR: Invalid choice. Please enter 1-4.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main_menu()