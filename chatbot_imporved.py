import os
import fitz  
import pickle
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from tavily import TavilyClient

os.environ["TAVILY_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"

def load_pdfs_from_drive(drive_folder_path):
    pdf_files = []
    for root, dirs, files in os.walk(drive_folder_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def extract_text_from_pdfs_parallel(pdf_paths):
    def process_pdf(path):
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return path, text

    pdf_texts = {}
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_pdf, pdf_paths)
        for path, text in results:
            pdf_texts[path] = text
    return pdf_texts

def cache_pdf_texts(pdf_texts, cache_path="pdf_cache.pkl"):
    with open(cache_path, "wb") as cache_file:
        pickle.dump(pdf_texts, cache_file)

def load_cached_texts(cache_path="pdf_cache.pkl"):
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as cache_file:
            return pickle.load(cache_file)
    return {}

def extract_text_from_pdfs(pdf_paths, cache_path="pdf_cache.pkl"):
    cached_texts = load_cached_texts(cache_path)
    remaining_files = [path for path in pdf_paths if path not in cached_texts]

    if remaining_files:
        new_texts = extract_text_from_pdfs_parallel(remaining_files)
        cached_texts.update(new_texts)
        cache_pdf_texts(cached_texts, cache_path)

    return cached_texts

def tavily_search_tool(query):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    result = client.search(query, search_depth="advanced")["results"]
    return result

def search_in_pdfs_tool(query, pdf_texts):
    for file, content in pdf_texts.items():
        if query.lower() in content.lower():
            return f"PDF에서 찾음 ({file}):\n{content}"
    return "해당 PDF에서 관련 정보를 찾을 수 없습니다."

def initialize_react_tools(pdf_texts):
    pdf_search_tool_instance = Tool(
        name="search_pdfs",
        func=lambda query: search_in_pdfs_tool(query, pdf_texts),
        description=(
            "PDF 문서에서 관련 정보를 검색합니다. "
            "인기있는 특정 도시(여행지)에 대해 현지 음식점, 여행 팁 등의 내용을 PDF 데이터를 기반으로 검색합니다."
        ),
    )
    tavily_search_tool_instance = Tool(
        name="search_tavily",
        func=tavily_search_tool,
        description=(
            "최신 트렌드, 실시간 정보, 이벤트 등을 검색합니다. "
            "PDF에 관련 정보가 없는 경우 주로 사용되며, "
            "유명 장소, 이벤트, 실시간 데이터를 제공합니다."
        ),
    )
    return [pdf_search_tool_instance, tavily_search_tool_instance]

def initialize_react_agent(tools):
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="conversational-react-description",
        memory=memory,
        verbose=True,
        handle_parsing_errors=True, 
    )
    return agent

def generate_schedule_response(agent, user_information, user_detail, user_message):
    prompt = f"""
    당신은 여행 계획 전문가입니다. 사용자가 여행 계획을 요청하면 PDF 데이터와 인터넷 검색 도구를 활용하여 최고의 계획을 생성하십시오.

    ### 사용자 정보:
    - 사용자 기본 정보: {user_information}
    - 사용자 디테일 정보: {user_detail}

    ### 사용자 요청:
    {user_message}

    ### 도구 사용 가이드:
    1. **PDF 데이터 검색**:
       - 특정 도시(예: 도쿄, 방콕, 다낭 등)에 대한 상세 정보는 PDF 파일에서 검색합니다.
       - PDF 데이터에는 숨겨진 관광지, 현지 음식점, 여행 팁 등이 포함되어 있습니다.
       - PDF에 관련 정보가 없을 경우, Tavily 검색 도구를 사용합니다.

    2. **Tavily 검색 도구**:
       - 실시간 정보나 최신 트렌드, 이벤트 정보를 검색합니다.
       - 예를 들어, 계절에 따른 축제나 최근에 새로 생긴 관광지에 대한 정보를 제공합니다.

    **주의**: 아래의 형식을 정확히 따르세요. 형식 오류가 있으면 재작성합니다.
    ### 형식:
    1. 여행 일정 계획을 요청한다면 무조건 이 형식을 따라야 합니다. 즉 다른 요청시에는 이 형식을 지킬 필요가 없습니다.
    2. 각 일정은 "n일차"로 나누어서 표시합니다.
    3. 각 일정에는 시간, 장소, 이동수단, 팁(선택 사항)을 포함합니다.
    4. 일정은 구조적으로 표시하며, 예시는 다음과 같습니다:

    ###1일차
    **오전 08:00** 신주쿠 가든 구경
    (팁: 아침 일찍 가면 덜 붐빕니다)

    ↓ 버스 15번 이용
    ---------------------------------------------------------
    **오후 01:00** 아사쿠사 사찰 방문

    ↓ 도보로 이동
    ---------------------------------------------------------
    **오후 05:00** 스카이트리 전망대

    ### 형식:
    1. 사용자가 준비물 안내를 요청하면 답변합니다.
    2. 사용자가 요청을 하지 않으면 답변하지 않아도 됩니다.
    3. 예시는 다음과 같습니다:

    ###준비물
    1. **여권 및 여행 관련 서류**: 해외 여행을 위해서 필수입니다. 필요한 서류나 문서를 챙기세요.
    2. **편한 신발**: 도쿄 여행은 도보 이동이 많아 편안한 신발이 필수입니다.
    3. **가벼운 외투**: 1월의 도쿄는 추울 수 있으니 따뜻한 옷을 준비하세요.
    4. ...
    """
    response = agent.invoke(prompt)
    output = response['output']
    return output

# Main
def implementation(user_information, user_detail, user_message, agent=None, folder_path=None):
    pdf_files = load_pdfs_from_drive(folder_path) 
    pdf_texts = extract_text_from_pdfs(pdf_files)  

    if agent is None:
        tools = initialize_react_tools(pdf_texts) 
        agent = initialize_react_agent(tools) 

    bot_message = generate_schedule_response(agent, user_information, user_detail, user_message)  # 일정 생성
    return bot_message
