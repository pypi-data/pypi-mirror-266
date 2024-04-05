from unstructured.partition.pdf import partition_pdf

class DocumentExtractor:
    """
    A class for extracting data from a parsed PDF document.
    """

    def __init__(self, file_path:str):
        self.file_path = file_path

    def extract_data(self):
        """
        Extracts data from the loaded document content (list of images).

        Args:
            document_content (list): A list of PIL Image objects representing the converted pages.

        Returns:
            str: A string containing the extracted data.

        Raises:
            Exception: If an error occurs during extraction.
        """

        try:

            elements = partition_pdf(filename=self.file_path) 
            extracted_text = ''.join([str(element) for element in elements])
            return extracted_text

        except Exception as e:
            raise Exception(f"Error during data extraction: {e}")
        
