import json
import re

# Define the text extraction agent
class TextExtractionAgent:
    def extract_text(self, textract_data):
        blocks = textract_data.get('Blocks', [])
        return [block['Text'].strip() for block in blocks if block['BlockType'] == 'LINE']

# Define the pattern recognition agent
class PatternRecognitionAgent:
    def recognize_address(self, text, address):
        # Use regex to detect address components
        # Allow for variations in street, city, state, and zip
        street_pattern = r"(\d+\s[A-Za-z0-9\s]+(?:Street|St|Ave|Avenue|Blvd|Road|Lane|Drive|Court))"
        city_state_pattern = r"([A-Za-z\s]+),\s([A-Za-z]{2})"
        zip_pattern = r"(\d{5}|\d{5}-\d{4})"

        # Only process if address has not been fully found yet (if any field is still None)
        if address["street"] and address["city"] and address["state"] and address["zip"]:
            return address  # No need to continue matching if the address is already filled

        #print(f"Attempting to match address in text: {text}")  # Debugging output
        
        street_match = re.search(street_pattern, text)
        if street_match and not address["street"]:
            address["street"] = street_match.group(1)
            #print(f"Street matched: {address['street']}")  # Debugging output

        city_state_match = re.search(city_state_pattern, text)
        if city_state_match and not address["city"]:
            address["city"] = city_state_match.group(1)
            address["state"] = city_state_match.group(2)
            #print(f"City matched: {address['city']}, State matched: {address['state']}")  # Debugging output

        zip_match = re.search(zip_pattern, text)
        if zip_match and not address["zip"]:
            address["zip"] = zip_match.group(1)
            #print(f"Zip matched: {address['zip']}")  # Debugging output

        return address

    def recognize_sections(self, text):
        # Match section titles
        section_titles = ["Purpose", "Scope", "Responsibility", "Procedure"]
        for title in section_titles:
            if title.lower() in text.lower():
                return title, text
        return None, None

    def recognize_date(self, text):
        # Improved regex to capture more date formats (e.g., Month Day, Year, MM/DD/YYYY)
        date_pattern = r"(DATE|Date)[\s:]*([A-Za-z]{3,9}\s\d{1,2},\s\d{4}|[0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{1,2}\s[A-Za-z]{3,9}\s[0-9]{4})"
        date_match = re.search(date_pattern, text)
        if date_match:
            #print(f"Date found: {date_match.group(2)}")  # Debug print to verify date capture
            return date_match.group(2)  # Return the date part
        return None

# Define the context understanding agent
class ContextUnderstandingAgent:
    def identify_section(self, text, previous_section):
        if previous_section and text.startswith("1."):
            return True
        return False

# Define the content structuring agent
class ContentStructuringAgent:
    def structure_content(self, text_blocks, address, date, sections):
        result = {
            "document_metadata": {
                "title": "DOCUMENT CONTROL SOP",
                "date": date
            },
            "address": address,
            "sections": []
        }

        # Initialize section_text correctly before appending content
        section_text = ""  # Ensure section_text starts as an empty string

        # Filter out only the relevant sections
        for section in sections:
            if section["title"] and section["text"]:
                result["sections"].append({
                    "title": section["title"],
                    "text": section["text"]
                })

        return result


# Main Execution Flow

def main():
    # Example input (Textract output)
    textract_data = json.load(open('docs/SOP_Document_Control.json'))

    # Create agents
    text_extraction_agent = TextExtractionAgent()
    pattern_recognition_agent = PatternRecognitionAgent()
    context_understanding_agent = ContextUnderstandingAgent()
    content_structuring_agent = ContentStructuringAgent()

    # Step 1: Extract raw text
    text_blocks = text_extraction_agent.extract_text(textract_data)

    # Debugging output: Print extracted text blocks
    #print("Extracted Text Blocks:")
    for block in text_blocks:
        #print(block)
        pass

    # Step 2: Recognize address information
    address = {"street": None, "city": None, "state": None, "zip": None}

    for block in text_blocks:
        address = pattern_recognition_agent.recognize_address(block, address)
        if all(address.values()):  # Check if all address fields are filled
            break  # Stop further address matching once it's fully found

    # Step 3: Recognize date
    date = None
    for block in text_blocks:
        date = pattern_recognition_agent.recognize_date(block)
        if date:
            break  # Stop once the date is found

    # Debugging output for the address and date
    #print("Extracted Address:", address)
    #print("Extracted Date:", date)

    # Step 4: Recognize sections and context
    sections = []
    current_section = None
    section_text = ""  # Initialize section_text as an empty string

    for block in text_blocks:
        section_title, section_content = pattern_recognition_agent.recognize_sections(block)
        
        # If we find a new section title, handle the previous section
        if section_title and current_section != section_title:
            if current_section:
                sections.append({"title": current_section, "text": section_text.strip()})
            current_section = section_title
            section_text = section_content.strip() if section_content else ""  # Initialize section_text
        elif current_section:
            section_text += " " + block.strip()

    # Handle the last section after loop
    if current_section:
        sections.append({"title": current_section, "text": section_text.strip()})

    # Step 5: Structure the content
    structured_data = content_structuring_agent.structure_content(text_blocks, address, date, sections)

    # Output the structured data
    print(json.dumps(structured_data, indent=4))

if __name__ == "__main__":
    main()
