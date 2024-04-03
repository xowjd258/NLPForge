import os

from langchain_core.prompts import PromptTemplate

def read_prompt():
    """
    Reads all '.prompt' files in the specified directory and returns a dictionary
    with filenames (without the extension) as keys and file contents as values.
    """
    prompts = {}
    # 현재 스크립트의 절대 경로를 구합니다.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_store_path = os.path.join(script_dir, 'prompt_store')  # prompt_store의 정확한 경로를 설정합니다.

    # os.walk를 사용하여 주어진 디렉토리 및 하위 디렉토리를 탐색합니다.
    for root, dirs, files in os.walk(prompt_store_path):
        for file in files:
            if file.endswith(".prompt"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                prompts[os.path.splitext(file)[0]] = content
    return prompts

def local_hub_pull(prompt_nm):
    prompts_dic = read_prompt()
    prompt = PromptTemplate.from_template(prompts_dic[prompt_nm])
    return prompt

if __name__ == '__main__':
    print(read_prompt())
