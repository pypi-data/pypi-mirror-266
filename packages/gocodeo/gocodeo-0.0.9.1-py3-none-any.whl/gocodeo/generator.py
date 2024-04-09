import sys
import os
from vertexai.language_models import CodeGenerationModel
from google.oauth2 import service_account
import vertexai
import re
import json
import requests
from dotenv import load_dotenv

import certifi
ca = certifi.where()

import pymongo
from pymongo import MongoClient

# credentials = service_account.Credentials.from_service_account_file("vertex-ai-service-account.json")
# load_dotenv(dotenv_path='.env')





credentials_data={
  "type": "service_account",
  "project_id": "symbolic-bit-398912",
  "private_key_id": "6cc13a1aa736855f25148aa6daa2f99374307180",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQClM+Eub91x2IhM\nMw5sID2+JwvHI9cRtE5BpIq13BXlN87z8gnKDUIfRQslGpg2pIk+IvizweKy8lmq\nOrA7XPLVFQl3JEvzq9xKbMAaLoOUS6rOf9ik157TPDw+m3JnL4VwNrjhplqWbU+X\nmCXc1hxdX2cm5SM2VZUE5vgco32/IKKvv511E6JUQSeFzB95/4XKkPO2xADcmams\n+6ngxJMRkuF6u1DZyWFkpCzYB/gCaX+HnHEiPm3doYOdb+i3fXuVBZ5y0V2zEcpz\nZeDpbZO7hmWQxPOnjCLWHbqIeCJreDbDdHMelkyv67g1Q9NRwTCLb8RfmeGzMvTo\nv9KJkr0pAgMBAAECggEAARo3hnfN99SEvv1tkIsmiP5PCyUnakF/GYZfkUHGuPYx\nC1pcy7G1nz/MCJNaMK3TEfcUcclOxKLutj7DWPdl0huHKfm0CAw9jBbtsT8I4b8f\nhKvrENk01h6wyDor/pmdP60dzrkCzGjY/x9PdrR3EVMcUnDKVgfRgWwz0P0bpGAw\nnrl6OkOMlQX2Psk0ekWI/WS5Tvt4G3P5VJNeoOdtRQEKvR+qaR3CIJyGafX0RrE8\n0PT2bYUeRP3A2+p1Si7Y6j3E/Kor+mwOjzro2Yl5eANwZMc3sYRxB3hKKAv5StNB\njU804hfJkfMGn46yy1altAUG9s9bq4P+qllgko7+AQKBgQDhrtm/JUAoUh7ew3c6\n89L5rtqZIdZkDoyTFEqQEhu1pN+RILL5J5TLtACmCzBFnW0VNfh0B5bDCuRlstoU\nNK5bdeeQmmeZmP617XB4rakKw0yrOMdu77+RMaGPegVr/bs5xgQjPg5iOrxIEL0r\nduaWYVp5wjW+YksFzmGEu1NIlQKBgQC7ZSIwahplYWzb1WKXj+wy+rWNfEce/yyh\nM5lfHEknUZdd6cu8s6rhkjVEkIeO5OFiylr7pqDEH/5gD6r6YSr4db25sFH5m51u\nsl3yHk9Dam0AdeBdQ21rc1Khfl8ycuFzSwsgSYEWtZ3uoWkud6spxiS3Mqp9uz+i\nBgz75Fs5RQKBgBvSITemEO2nifSuJfGXgyeSfZIpELPO81diRfrSsKXIyGKspEOA\ntKAT9YyCjpXWXU8jExjCorwyiItc6/NXtzLBKyWxUxolOSkWNyo5RkB0aOwmmLc9\nSOFOO/ti8G4qnjz2AyaRDNbhJLrBjYBhLPXW1H90CIoKtfLmSTFConatAoGBAIfH\nDk+gAUIlphdedBI28MA7UWKTgoCeCTs/xMfaGdMIVjFwnfM7Bvxr0Ha+dcn+YqQO\n1H9zyxZvzALUN2E1GEpwHSi27Z56t0YmrNUqSuog6ZukzQ0mNtjc9SkYBGfsPxgn\nbodVWtgWfbkScMB/aqBY9e9bIZb6HnAKDExSuBo1AoGAJnAsYFHyeDs8ZFaVGhPO\nGeYXTMj9JGwZHR+wqFfuiBIqs/cra3xETIDyr6cGT9xTjQ0nVazvROBANgkU+YIO\nWxzzc77PnpfP20yMMTNsJFoZhSQUns8LY9hxzKSnPYURqf32HTTImmmCbz2RJAyO\nOvPWkmJDkDvalolS6HNnEPE=\n-----END PRIVATE KEY-----\n",
  "client_email": "vertex-ai-service-account@symbolic-bit-398912.iam.gserviceaccount.com",
  "client_id": "114836232517254252283",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vertex-ai-service-account%40symbolic-bit-398912.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
credentials = service_account.Credentials.from_service_account_info(credentials_data)

vertexai.init(
    project="symbolic-bit-398912",
    location="us-central1",
    credentials=credentials
)


# GoCodeo_URL = "http://127.0.0.1:5000/api/v1/explain_api"


GoCodeo_URL = "https://staging-ai-service.gocodeo.com/api/v1/explain_api"

CHAT_API_URL = "https://api.openai.com/v1/chat/completions"
HEADERS = {
    'Content-Type': 'application/json'
}



# MongoDB connection URL
connection_url = "mongodb+srv://mohantysoumendraprasad15:roman2003@cli.e4umg8e.mongodb.net/"

# Initialize MongoDB client
client = MongoClient(connection_url,tlsCAFile=ca)

# Access the CLI database
db = client["CLI"]

def update_client_1(private_key, total_lines, total_functions):
    # Access the client_1 collection
    # collection = db["client_1"]
    collection=db["Local_1"]

    # Check if private_key matches
    if private_key == "gc_local":
        # Find the document with the private_key
        document = collection.find_one({"private_key": private_key})

        # If document exists, update the lines and functions values
        if document:
            previous_lines = document.get("lines", 0)
            previous_functions = document.get("functions", 0)
            new_lines = previous_lines + total_lines
            new_functions = previous_functions + total_functions
            collection.update_one(
                {"private_key": private_key},
                {"$set": {"lines": new_lines, "functions": new_functions}},
            )
            # print("Updated lines:", new_lines)
            # print("Updated functions:", new_functions)
        else:
            # If document doesn't exist, insert a new document with the lines and functions values
            collection.insert_one(
                {
                    "private_key": private_key,
                    "lines": total_lines,
                    "functions": total_functions,
                }
            )
            # print("Inserted new document with lines and functions:", total_lines, total_functions)
    else:
        print("Authentication failed. Private key doesn't match.")
def extract_function_names(code):
    # Regular expression to match function names
    function_name_regex = r'(?<!\.)\b(\w+)\s*\([^)]*\)(?:\s*:\s*\w+)?\s*{'

    # Find all function names in the code
    function_names = re.findall(function_name_regex, code)
    

    # List of keywords associated with conditional blocks, loops, and nested functions
    keywords_to_exclude = ['if', 'else', 'for', 'while', 'else if', 'switch', 'function', 'ngOnChanges', 'ngOnInit', 'ngDoCheck', 'ngAfterContentInit', 'ngAfterContentChecked', 'ngAfterViewInit', 'ngAfterViewChecked', 'ngOnDestroy','constructor']


    # Filter out unwanted function names
    filtered_names = [name for name in function_names if name not in keywords_to_exclude]

    return filtered_names





def extract_function_code(code, method_name):
    counter=0
    method_code = []
    in_method = False
    opening_braces = 0
    closing_braces = 0

    # Start and end markers for the method
    start_marker = f"{method_name}("
    end_marker = "}"

    # Iterate through each line of the code
    for line in code.split('\n'):
        
        # Check if the line contains the start of the current method
        if start_marker in line:
            in_method = True
            method_code.append(line.strip())
            opening_braces += line.count('{')
            closing_braces += line.count('}')

        # Check if we're inside the current method
        elif in_method:
            counter+=1
            # Add the line to the method code
            method_code.append(line.strip())
            opening_braces += line.count('{')
            closing_braces += line.count('}')

            # Check if we've reached the end of the method
            if opening_braces > 0 and opening_braces == closing_braces:
                in_method = False
                

    # Join the lines of the method code
    method_code = '\n'.join(method_code)
    
    return method_code,counter





def explain_api_request(code):
   
    prompt =f"You are angularjs unit testing expert. Your job is to first understand the given code {code} then explain the code so that every team member should understand the logic and working of the function"
    payload = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.6
    }


    response = requests.post(GoCodeo_URL, json=payload, headers=HEADERS)


    if response.status_code != 200:
        raise Exception(response.text)
  
    choices = response.json()

    if len(choices) == 0:
        raise Exception("Prompt did not return any answer")   
    message = choices[0].get("message", {}).get("content", "")
    # print(message, "message")
 
    return message

def open_api_request(code, type, number, context):
   
    prompt = f"You are angularjs unit testing expert. Your job is to write {number} numbers of {type} type sceanrios for the given code {code} using the explaination of its working here {context}. Your job is to achieve maximum code coverage.Generate scenarios from the given {context} only. It is mandatory that each  numbers of {type} type scenarios genereated by you should be different from each other , means not alike / same type. Try to cover all the possible different corner cases in these scenarios."
    payload = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.8
    }

    response = requests.post(GoCodeo_URL, json=payload, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(response.text)
  
    choices = response.json()

    if len(choices) == 0:
        raise Exception("Prompt did not return any answer")   
    message = choices[0].get("message", {}).get("content", "")
    # print(message, "message")
 
    return message
def generate_api_request(code, context, type, number,import_lines,imported_code):
    prompt = f"You are angularjs unit testing expert. Your job is to write {number} numbers high quality unit test code using jasmine and karma framework only, for given angular code: {code} for the given {type} scenarios in the context: {context}. Strictly go through the context and generate at least {number} numbers high quality unit test code with description including assertions covering all scenarios in one file. Please mock all the services and data where ever necessary. Please Make sure to import all the dependencies at the top for execution of tests & the imports are {import_lines}.Import all these dependencies as per given if they are present.{imported_code}these are the code of imported classes or functions.Take context from here also & try to generate more accurate & executable unit test cases."

    payload = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.8
    }

    response = requests.post(GoCodeo_URL, json=payload, headers=HEADERS)
   
    if response.status_code != 200:
        raise Exception(response.text)
  
    choices = response.json()

    if len(choices) == 0:
        raise Exception("Prompt did not return any answer")   
    message = choices[0].get("message", {}).get("content", "")
    # print(message, "message")
 
    return message      

def generate_api_request1(code, response, type, number):
    prompt = f"You are angularjs unit testing expert.Here is the current generated unit test cases:{response}, for input code:{code} . Your task is to improve code of all these current unit test cases on {type} type scenarios. If the  unit test cases you are getting that are  partially implemented ,then you have to fully implement it  accurately using jasmine and karma framework .It is mandatory that every unit test cases should be implemented completely."
    # print(prompt)
    try:
        prompt1 = prompt
        parameters = {
    "max_output_tokens": 8000,
    "temperature": 0.8
}
        model = CodeGenerationModel.from_pretrained("code-bison-32k")
        response = model.predict(
            prefix=prompt1,
            **parameters
        )
        return response.text

    except Exception as e:
        # Handle exceptions and return None
        print(f"Exception: {e}")
        return None
    


def extract_filename(file_path):
    # Convert the file path to raw string format
    file_path = rf"{file_path}"

    # Extract the filename from the file path
    filename = os.path.basename(file_path)

    # Remove the file extension if present
    filename_without_extension = os.path.splitext(filename)[0]

    

    return filename_without_extension    

def extract_imports_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            typescript_code = file.read()
            
            # Regular expression pattern to match import statements
            import_pattern = r'import\s+{[^}]+}\s+from\s+[\'"].+?[\'"];'

            # Find all import statements using regex
            import_lines = re.findall(import_pattern, typescript_code)

            if not import_lines:
                return ""  # Return empty string if no import lines found

            # Concatenate import lines into a single string with newline characters
            import_string = '\n'.join(import_lines)
            
            return import_string
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"Error: {e}"
    
# Handle user defined imports
def extract_user_defined_imports(typescript_code):
    if not typescript_code.strip():
        return ''  # Return empty string if no imports found

    # Regular expression pattern to match import blocks
    import_pattern = r'(import\s+{[^}]+}\s+from\s+[\'"][^\'"]+[\'"];)+'

    # Find all import blocks using regex
    import_blocks = re.findall(import_pattern, typescript_code)

    user_defined_imports = []

    # Iterate through import blocks
    for import_block in import_blocks:
        # Regular expression pattern to match individual import statements within the block
        import_statement_pattern = r'import\s+{([^}]+)}\s+from\s+[\'"]([^\'"]+)[\'"];'

        # Find all import statements within the block
        import_statements = re.findall(import_statement_pattern, import_block)

        # Iterate through import statements within the block
        for import_statement in import_statements:
            import_symbols, import_path = import_statement

            # Check if the import path is a relative path (starts with './' or '../')
            if import_path.startswith('./'):
                # Replace './' with '../'
                import_path = '../' + import_path[2:]
            elif import_path.startswith('../'):
                # Add an extra '../' to the import path
                import_path = '../' + import_path

            # Construct the new import statement
            new_import_statement = f"import {{ {import_symbols} }} from '{import_path}';"

            # Append the new import statement to the list
            user_defined_imports.append(new_import_statement)

    # Join the user-defined imports into a single string
    user_defined_imports_string = '\n'.join(user_defined_imports)

    return user_defined_imports_string




# Replace the updated imports 
def replace_string_imports(original_code, updated_imports):
    if not original_code.strip() or not updated_imports.strip():
        return original_code  # Return original code if no imports found

    try:
        # Regular expression pattern to match import statements
        import_pattern = r'import\s+{[^}]+}\s+from\s+[\'"][^\'"]+[\'"];\n*'

        # Find and remove existing imports
        existing_imports = re.findall(import_pattern, original_code)
        original_code = re.sub(import_pattern, '', original_code)

        # Prepend new imports before the remaining code
        updated_code = '\n'.join([import_line.strip() for import_line in updated_imports.split('\n')]) + '\n\n' + original_code.strip()

        return updated_code
    except Exception as e:
        return f"Error: {e}"

# Context retrival from file
def fetch_imported_code(import_statement_string, base_path):
    # Regular expression pattern to match user-defined import statements
    user_import_statement_pattern = r'import\s+{([^}]+)}\s+from\s+[\'"](\.\./[^\'"]+)[\'"];'

    # Find all user-defined import statements using regex
    user_import_statements = re.findall(user_import_statement_pattern, import_statement_string)
    user_import_statements = [(import_symbols.strip(), import_path.strip()) for import_symbols, import_path in user_import_statements]
    
    imported_code = []

    # Iterate through user-defined import statements
    for import_symbols, import_path in user_import_statements:
        # Construct the file path based on the base path and the import path
        file_path = os.path.abspath(os.path.join(base_path, import_path + '.ts'))

        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        # Read the content of the file
        with open(file_path, 'r') as file:
            file_content = file.read()

            # Split import symbols into individual imports
            import_symbols_list = [symbol.strip() for symbol in import_symbols.split(',')]

            # Iterate through individual imports
            for symbol in import_symbols_list:
                # Check if the imported item is a class or a function
                is_class = re.search(rf'\bclass\s+{symbol}\b', file_content)
                is_function = re.search(rf'\bfunction\s+{symbol}\b', file_content)

                # Extract the code of the imported item
                imported_item_code = None
                if is_class:
                    class_code_pattern = rf'\bexport\s+class\s+{symbol}\b[\s\S]*?(?=export\s+class|\Z)'
                    class_code_match = re.search(class_code_pattern, file_content)
                    if class_code_match:
                        imported_item_code = class_code_match.group(0).strip()
                elif is_function:
                    function_code_pattern = rf'\bexport\s+function\s+{symbol}\b[\s\S]*?(?=export\s+function|\Z)'
                    function_code_match = re.search(function_code_pattern, file_content)
                    if function_code_match:
                        imported_item_code = function_code_match.group(0).strip()

                if imported_item_code:
                    imported_code.append(imported_item_code)
                else:
                    print(f"Class or function '{symbol}' not found in file: {file_path}")

    # Join all the imported code strings into a single string
    all_imported_code = '\n\n'.join(imported_code)

    return all_imported_code

# for gettting code of happy path & negative cases scenarios
def generate_tests(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            file_content = file.read()

            file_size = os.path.getsize(file_name)

            function_names = extract_function_names(file_content)
            total_line=[]
            

            # Prompt user for private key
            private_key = input("Enter your private key: ")
            
            if private_key == "gc_local":

            
                function_names = extract_function_names(file_content)
                # print("Function Names:", function_names)

                import_lines=extract_imports_from_file(file_name)
                new_imports = extract_user_defined_imports(import_lines)
                # print(new_imports)
                
                # Extract function code for each function name
                for function_name in function_names:
                    function_code,lines = extract_function_code(file_content, function_name)
                    lines=lines-1
                    # print("\nFunction:", function_name)
                    # print("Code:\n", function_code)
                    # print(lines)
                    total_line.append(lines)


             

                # Check if the provided private key matches the expected key
                if file_size >= 20000:
                    print("Function Names:", function_names)

                    # Extract function code for each function name
                    for function_name in function_names:
                        function_code = extract_function_code(file_content, function_name)
                        # print("\nFunction:", function_name)
                        # print("Code:\n", function_code)

                        behaviour_type = [{"type": "HappyPath", "number": 6}, {"type": "EdgeCase", "number":18 }, {"type": "NegativeCase", "number": 8}]

                        explain_response = explain_api_request(function_code)

                        for obj in behaviour_type:
                            
                            type = obj['type']
                            print(f"Generating tests on '{type}' scenarios for '{function_name}' function")
                            api_response = open_api_request(function_code, obj['type'], obj['number'], explain_response)

                            directory_path = os.path.dirname(file_name)
                            test_folder_path = os.path.join(directory_path, 'gocodeo_tests')
                            function_test_folder_path = os.path.join(test_folder_path, function_name)
                            output_file_path = os.path.join(function_test_folder_path, f'test_{function_name}_{type}.spec.ts')

                            retrived_context=fetch_imported_code(new_imports,function_test_folder_path)
                            # print(retrived_context)
                                

                            test_response = generate_api_request(function_code, api_response, obj['type'], obj['number'],import_lines,retrived_context)
                            test_response1 = generate_api_request1(function_code, test_response,obj['type'], obj['number'])
        
                        
                            if test_response1:
                                directory_path = os.path.dirname(file_name)
                                test_folder_path = os.path.join(directory_path, 'gocodeo_tests')
                                os.makedirs(test_folder_path,exist_ok=True)
                                function_test_folder_path = os.path.join(test_folder_path, function_name)
                                os.makedirs(function_test_folder_path,exist_ok=True)
                                
                                # Write API response (test cases) to a test.py file in the same directory
                                output_file_path = os.path.join(function_test_folder_path, f'test_{function_name}_{type}.spec.ts')
                                
                                pattern1 = r'(?:\s*```(?:typescript|javascript|ts)?\n)?(.*?)(?:```|$)'
                                pattern2 = r'```(?:typescript|javascript|ts)?\n(.*?)```|\b(?:typescript|javascript|ts)?\n(.*?)(?=$|```)'
                                combined_pattern = f"{pattern1}|{pattern2}"


                                match = re.search(combined_pattern, test_response1, re.DOTALL)

                                if match:
                                    content = match.group(1) or match.group(2) or match.group(3) or match.group(4)
                                    content=content.strip()
                                else:
                                    content=test_response1
                                updated_code=replace_string_imports(content, new_imports)
                                with open(output_file_path, 'w') as output_file:
                                    output_file.write(updated_code)
                                    print(f"Test cases for '{function_name}' written to {output_file_path}")
                            else:
                                print(f"Failed to fetch test cases from API for function '{function_name}'.")        
                            
                    total_lines=sum(total_line) 
                 
                    total_functions=len(function_names)
                
                    # update_client_1(private_key, total_lines,total_functions)
                else:
                    explain_response = explain_api_request(file_content)
                    File_name=extract_filename(file_name)
                    
                    behaviour_type = [{"type": "HappyPath", "number": 6}, {"type": "EdgeCase", "number":12 }, {"type": "NegativeCase", "number": 8}]
                    for obj in behaviour_type:
                        type = obj['type']

                        print(f"Generating tests on '{type}' scenarios for file : {file_name} ")
                        api_response = open_api_request(file_content, obj['type'], obj['number'], explain_response)
                    
                        directory_path = os.path.dirname(file_name)
                        test_folder_path = os.path.join(directory_path, 'gocodeo_tests')
                        output_file_path = os.path.join(test_folder_path, f'test_{File_name}_{type}.spec.ts')

                        retrived_context=fetch_imported_code(new_imports,test_folder_path)
                        # print(retrived_context)

                        test_response = generate_api_request(file_content, api_response, obj['type'], obj['number'],import_lines,retrived_context)
                        
                        test_response1 = generate_api_request1(file_content, test_response,obj['type'], obj['number'])  
                        if test_response1:

                            directory_path = os.path.dirname(file_name)
                            test_folder_path = os.path.join(directory_path, 'gocodeo_tests')
                            os.makedirs(test_folder_path,exist_ok=True)
                            
                            # Write API response (test cases) to a test.py file in the same directory
                            output_file_path = os.path.join(test_folder_path, f'test_{File_name}_{type}.spec.ts')
                            
                            pattern1 = r'(?:\s*```(?:typescript|javascript|ts)?\n)?(.*?)(?:```|$)'
                            pattern2 = r'```(?:typescript|javascript|ts)?\n(.*?)```|\b(?:typescript|javascript|ts)?\n(.*?)(?=$|```)'
                            combined_pattern = f"{pattern1}|{pattern2}"


                            match = re.search(combined_pattern, test_response1, re.DOTALL)

                            if match:
                                content = match.group(1) or match.group(2) or match.group(3) or match.group(4)
                                content=content.strip()
                            else:
                                content=test_response1
                            updated_code=replace_string_imports(content, new_imports)
                            with open(output_file_path, 'w') as output_file:
                                output_file.write(updated_code)
                                print(f"Test cases on '{type}' scenarios written to file:{output_file_path}")
                        else:
                            print(f"Failed to fetch test cases from API for function '{function_name}'.")        
            else:
                print("Invalid private key. Access denied.")

    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")

def generate_tests_cli():
    if len(sys.argv) != 3:
        print("Usage: gocodeo generate <file_name>")
        sys.exit(1)
    
    file_name = sys.argv[2]
    generate_tests(file_name)

if __name__ == "__main__":
    generate_tests_cli()