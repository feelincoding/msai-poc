import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import io
import os
import zipfile
import shutil
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.retrievers import AzureAISearchRetriever
import xml.etree.ElementTree as ET



load_dotenv(override=True)
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
AZURE_STORAGE_NAME = os.getenv("AZURE_STORAGE_NAME")
AZURE_STORAGE_CONNECTION_KEY = os.getenv("AZURE_STORAGE_CONNECTION_KEY")

OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SEARCHSERVICE_NAME = os.getenv("SEARCHSERVICE_NAME")
SEARCHSERVICE_KEY = os.getenv("SEARCHSERVICE_KEY")
SEARCHSERVICE_ENDPOINT = os.getenv("SEARCHSERVICE_ENDPOINT")
SEARCHSERVICE_INDEX_NAME = os.getenv("SEARCHSERVICE_INDEX_NAME")
SEARCHSERVICE_EMBEDDING_DEPLOYMENT_NAME = os.getenv("SEARCHSERVICE_EMBEDDING_DEPLOYMENT_NAME")

def init_session_state():
    """세션 상태 초기화"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'page1'
    
    if 'project_config' not in st.session_state:
        st.session_state.project_config = {
            'project_name': '',
            'group_id': '',
            'artifact_id': '',
            'package_name': '',
            'description': '',
            'java_version': '17',
            'spring_boot_version': '3.2.0',
            'architecture_type': 'monolithic',
            'architecture_pattern': 'mvc',
            'database': 'mysql',
            # 'csv_file': None,
            'additional_requirements': '',
            'structure': ''
        }

def render_project_metadata_section():
    """프로젝트 메타데이터 섹션"""
    st.subheader("📋 Project Metadata")
    
    col1, col2 = st.columns(2)
    
    with col1:
        group_id = st.text_input(
            "Group",
            value=st.session_state.project_config['group_id'],
            placeholder="com.example"
        )
        
        artifact_id = st.text_input(
            "Artifact",
            value=st.session_state.project_config['artifact_id'],
            placeholder="demo"
        )
        
        project_name = st.text_input(
            "Name",
            value=st.session_state.project_config['project_name'],
            placeholder="demo"
        )
    
    with col2:
        description = st.text_input(
            "Description",
            value=st.session_state.project_config['description'],
            placeholder="Demo project for Spring Boot"
        )
        
        package_name = st.text_input(
            "Package name",
            value=st.session_state.project_config['package_name'],
            placeholder="com.example.demo"
        )
    
    # 세션 상태 업데이트
    st.session_state.project_config.update({
        'group_id': group_id,
        'artifact_id': artifact_id,
        'project_name': project_name,
        'description': description,
        'package_name': package_name
    })

def render_project_settings_section():
    """프로젝트 설정 섹션"""
    st.subheader("⚙️ Project Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        java_version = st.selectbox(
            "Java Version",
            options=['8', '11', '17', '21'],
            index=2  # 기본값: 17
        )
    
    with col2:
        spring_boot_version = st.selectbox(
            "Spring Boot Version",
            options=['3.2.0', '3.1.5', '3.0.12', '2.7.17'],
            index=0  # 기본값: 3.2.0
        )
    
    with col3:
        packaging = st.selectbox(
            "Packaging",
            options=['Jar', 'War'],
            index=0
        )
    
    # 세션 상태 업데이트
    st.session_state.project_config.update({
        'java_version': java_version,
        'spring_boot_version': spring_boot_version,
        'packaging': packaging.lower()
    })

def render_architecture_section():
    """아키텍처 선택 섹션"""
    st.subheader("🏗️ Architecture Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Architecture Type**")
        architecture_type = st.radio(
            "Choose architecture type:",
            options=['monolithic', 'msa'],
            format_func=lambda x: {
                'monolithic': '🏢 Monolithic',
                'msa': '🔗 Microservices (MSA)'
            }[x],
            key="arch_type"
        )
        
        if architecture_type == 'monolithic':
            st.info("💡 Single deployable unit with all features in one application")
        else:
            st.info("💡 Distributed system with multiple independent services")
    
    with col2:
        st.write("**Architecture Pattern**")
        architecture_pattern = st.radio(
            "Choose architecture pattern:",
            options=['mvc', 'hexagonal'],
            format_func=lambda x: {
                'mvc': '🎯 MVC (Model-View-Controller)',
                'hexagonal': '⬡ Hexagonal (Ports & Adapters)'
            }[x],
            key="arch_pattern"
        )
        
        if architecture_pattern == 'mvc':
            st.info("💡 Traditional layered architecture with Controllers, Services, Repositories")
        else:
            st.info("💡 Clean architecture with domain at center, isolated from external concerns")
    
    # 세션 상태 업데이트를 여기로 이동
    st.session_state.project_config.update({
        'architecture_type': architecture_type,
        'architecture_pattern': architecture_pattern
    })

def render_database_section():
    """데이터베이스 선택 섹션"""
    st.subheader("🗄️ Database Configuration")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        database = st.selectbox(
            "Database Type",
            options=['mysql', 'postgresql', 'h2', 'mariadb'],
            format_func=lambda x: {
                'mysql': '🐬 MySQL',
                'postgresql': '🐘 PostgreSQL',
                'h2': '💾 H2 Database',
                'mariadb': '🦭 MariaDB'
            }[x]
        )
    
    with col2:
        db_info = {
            'mysql': "Popular open-source relational database",
            'postgresql': "Advanced open-source relational database with rich features",
            'h2': "Lightweight in-memory database, perfect for development and testing",
            'mariadb': "MySQL-compatible database with enhanced features"
        }
        st.info(f"💡 {db_info[database]}")
    
    # 세션 상태 업데이트
    st.session_state.project_config['database'] = database


def render_additional_requirements_section():
    """추가 요구사항 섹션"""
    st.subheader("📝 Additional Requirements & Entities")
    example = """
    Entity Name,Description,Primary Key,Foreign Keys (Relationships),Key Fields (for quick understanding)
    Users,쇼핑몰의 고객 또는 관리자 정보,id,,email, username, password_hash
    Products,판매되는 상품의 정보,id,category_id (Categories),name, price, stock_quantity
    Categories,상품을 분류하는 카테고리 정보,id,parent_id (Categories - Self-referencing),name
    Orders,고객의 주문 정보,id,user_id (Users),order_date, total_amount, status
    Order_Items,각 주문에 포함된 개별 상품의 상세 정보,id,order_id (Orders),product_id (Products),quantity, price_at_order
    """
    
    additional_requirements = st.text_area(
        "Describe any additional requirements or features:",
        value=st.session_state.project_config['additional_requirements'],
        # placeholder="예시:\n- JWT 인증 구현\n- Redis 캐싱 적용\n- API 문서화 (Swagger)\n- 단위 테스트 포함\n- Docker 컨테이너화",
        placeholder=f"예시:\n{example}",
        height=150
    )
    
    # 세션 상태 업데이트
    st.session_state.project_config['additional_requirements'] = additional_requirements

def render_page1():
    """Page 1: Spring Initializr 스타일 설정 페이지"""
    st.title("🚀 Spring Boot Project Generator")
    st.markdown("Generate your custom Spring Boot project with AI assistance")
    
    # 메인 컨테이너
    with st.container():
        # 왼쪽: 프로젝트 설정
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            render_project_metadata_section()
            st.divider()
            render_project_settings_section()
            st.divider()
            render_additional_requirements_section()
        
        with col_right:
            # 오른쪽: 아키텍처 및 데이터베이스 설정 (Spring Initializr의 dependencies 영역 대체)
            st.markdown("### 🎯 Configuration Panel")
            
            with st.container():
                render_architecture_section()
                st.divider()
                render_database_section()
                # st.divider()
                # render_csv_upload_section()
    
    # 하단 버튼
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔍 Preview Configuration", type="primary", use_container_width=True):
            # 필수 필드 검증
            config = st.session_state.project_config
            if not config['project_name'] or not config['group_id'] or not config['artifact_id'] or not config['package_name']:
                st.error("Please fill in the required fields: Project Name, Group, Artifact and Package Name.")
            else:
                st.session_state.current_page = 'page2'
                st.rerun()

def render_page2():
    """Page 2: 설정 확인 및 프로젝트 생성"""
    st.title("📋 Project Configuration Review")
    
    config = st.session_state.project_config
    
    # 프로젝트 정보 요약
    st.subheader("📊 Project Summary")
    
    # 기본 정보
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Basic Information**")
        st.write(f"• **Project Name:** {config['project_name']}")
        st.write(f"• **Group ID:** {config['group_id']}")
        st.write(f"• **Artifact ID:** {config['artifact_id']}")
        st.write(f"• **Package:** {config['package_name']}")
        st.write(f"• **Description:** {config['description']}")
    
    with col2:
        st.markdown("**⚙️ Technical Configuration**")
        st.write(f"• **Java Version:** {config['java_version']}")
        st.write(f"• **Spring Boot:** {config['spring_boot_version']}")
        st.write(f"• **Packaging:** {config.get('packaging', 'jar').title()}")
    
    # 아키텍처 정보
    st.subheader("🏗️ Architecture & Database")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        arch_icon = "🏢" if config['architecture_type'] == 'monolithic' else "🔗"
        st.markdown(f"**Architecture Type**\n{arch_icon} {config['architecture_type'].title()}")
    
    with col2:
        pattern_icon = "🎯" if config['architecture_pattern'] == 'mvc' else "⬡"
        st.markdown(f"**Architecture Pattern**\n{pattern_icon} {config['architecture_pattern'].upper()}")
    
    with col3:
        db_icons = {'mysql': '🐬', 'postgresql': '🐘', 'h2': '💾', 'mariadb': '🦭'}
        db_icon = db_icons.get(config['database'], '🗄️')
        st.markdown(f"**Database**\n{db_icon} {config['database'].title()}")
    
    # 추가 요구사항
    if config['additional_requirements']:
        st.subheader("📝 Additional Requirements & Entities")
        st.text_area(
            "Requirements:",
            value=config['additional_requirements'],
            height=100,
            disabled=True
        )
    
    # 프로젝트 구조 미리보기
    st.subheader("📁 Expected Project Structure")
    package_path = config['package_name'].replace('.', '/')
    # package_path = config['group_id'].replace('.', '/') + '/' + config['package_name'].replace('.', '/')
    
    structure = f"""
    {config['artifact_id']}/
    ├── src/
    │   ├── main/
    │   │   ├── java/
    │   │   │   └── {package_path}/
    │   │   │       ├── {(config['project_name'][:1].upper() + config['project_name'][1:] if config['project_name'] else config['project_name'])}Application.java
    │   │   │       ├── controller/
    │   │   │       ├── service/
    │   │   │       ├── repository/
    │   │   │       ├── entity/
    │   │   │       └── config/
    │   │   └── resources/
    │   │       └──  application.yml
    │   └── test/
    │       └── java/
    ├── build.gradle
    └── README.md
    """
    
    st.code(structure)
    st.session_state.project_config['structure'] = structure

    client = AzureOpenAI(
        api_version=OPENAI_API_VERSION,
        azure_endpoint=OPENAI_API_ENDPOINT,
        api_key=OPENAI_API_KEY,
    )
    index_name = SEARCHSERVICE_INDEX_NAME
    retriever = AzureAISearchRetriever(
        service_name=SEARCHSERVICE_NAME,
        top_k=3,
        index_name=index_name, # ai search 서비스에서 사용할 인덱스 이름
        content_key="chunk", # 검색된 결과에서 문서의 page_content로 사용할 키, 주의) 인덱스에서 검색대상될 필드 명이 아니다.
        api_key=SEARCHSERVICE_KEY # Azure Search Service 의 key
    )

    st.title("🧠 Pro-Gen 데모")
    # st.caption("💬 OpenAI GPT 모델을 사용하는 간단한 채팅 앱")

    # API 호출을 한 번만 실행하도록 세션 상태 체크
    if 'project_analysis_done' not in st.session_state:
        with st.spinner("프로젝트 분석 중..."):
            results = [d for d in retriever.invoke("ktds 개발 규칙")]
            response = client.chat.completions.create(
                model= OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": f"{results[0].page_content.replace("\\n", "\n").replace("\n", " ")}에 따라서 {st.session_state.project_config['additional_requirements']}를 수정하여라. 사용자에게 보여주는 값은 오직 entity만 나타내라."
                    }
                ],
                temperature=0.7,
            )
            print(response.choices[0].message.content)
            st.session_state.project_config['additional_requirements'] = response.choices[0].message.content

            response = client.chat.completions.create(
                model= OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": f"{st.session_state.project_config}를 보기 좋은 형태로 나타내고 불필요한 말은 빼라."
                    }
                ],
                temperature=0.7,
            )
            
            # 세션 상태에 프로젝트 정보 저장
            st.session_state.project_summary = response.choices[0].message.content

            response = client.chat.completions.create(
                model= OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": f"{response.choices[0].message.content}를 참고하여 생성할 파일에 경로를 포함하고 번호를 매겨 답변하라. 각 파일에 코드를 나타낼 필요는 없다.db는 h2를 사용하고, 프로젝트 구조에 있는 설정파일도 번호에 포함하라. build.gradle 파일도 포함하라."
                    }
                ],
                temperature=0.7,
            )
            assistant_reply = response.choices[0].message.content

            response = client.chat.completions.create(
                model= OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": f"{response.choices[0].message.content}를 참고하여 생성할 파일들을 모두 xml 형태로만 답변하고 불필요한 말은 빼라. 양식은 다음과 같다. '<total>file_count</total><file><number>1</number><path>pro-gen/src/com/poc/progen/controller/</path><name>OrderController</name></file>'"
                    }
                ],
                temperature=0.7,
            )
            print(f"생성할 파일의 경로: {response.choices[0].message.content}")
            xml_content = response.choices[0].message.content
            
            root = ET.fromstring(f"<root>{xml_content}</root>")

            # 전체 파일 개수 가져오기
            total_files = root.find('total').text
            print(f"Total files: {total_files}\n")

            # 각 'file' 엘리먼트 순회하며 정보 추출
            file_list = []
            for file_elem in root.findall('file'):
                number = file_elem.find('number').text
                path = file_elem.find('path').text
                name = file_elem.find('name').text
                
                file_info = {
                    'number': int(number),
                    'path': path,
                    'name': name
                }
                file_list.append(file_info)

            print("Files to be created:", file_list)
            
            # 세션 상태에 결과 저장
            st.session_state.file_list = file_list
            st.session_state.assistant_reply = assistant_reply
            st.session_state.project_analysis_done = True
    
    # 세션 상태에서 저장된 데이터 사용
    file_list = st.session_state.get('file_list', [])
    assistant_reply = st.session_state.get('assistant_reply', "")
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 다음과 같이 프로젝트를 생성은 ktds 개발 규칙을 따릅니다."},
            {"role": "system", "content": f"생성할 프로젝트는 다음과 같습니다. {st.session_state.get('project_summary', '')}"}
        ]
        if assistant_reply:
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    # 채팅 영역을 스크롤 가능한 컨테이너로 설정
    chat_container = st.container(height=400)  # 높이 약 5cm (400px)
    
    with chat_container:
        # 이전 대화 출력
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 하단 버튼
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Configuration", use_container_width=True):
            st.session_state.current_page = 'page1'
            st.rerun()
    
    with col3:
        if st.button("🚀 Generate Project", type="primary", use_container_width=True):
            try:
                generated_files = []
                target_folder = os.path.join(os.path.dirname(__file__), "target")
                
                for file_info in file_list:
                    # file_info['path']에 이미 프로젝트 구조가 포함되어 있으므로 직접 사용
                    project_folder = os.path.join(target_folder, file_info['path'].strip('/'))
                    
                    # 폴더 생성 (폴더가 없으면 생성)
                    os.makedirs(project_folder, exist_ok=True)
                    
                    # 파일 생성
                    java_file_path = os.path.join(project_folder, f"{file_info['name']}")

                    # AI로 파일 내용 생성
                    response = client.chat.completions.create(
                        model= OPENAI_DEPLOYMENT_NAME,
                        messages=[
                            {
                                "role": "user",
                                "content": f"{st.session_state.project_summary}와 {file_list}를 참고하여 {file_info['name']} 파일 안에 들어갈 코드만 답변하라. ```language```는 제외하라."
                            }
                        ],
                        temperature=0.7,
                    )
                    java_content = f"""{response.choices[0].message.content}"""
                    
                    # 파일 쓰기
                    with open(java_file_path, 'w', encoding='utf-8') as f:
                        f.write(java_content)
                    
                    generated_files.append({
                        'path': java_file_path,
                        'name': file_info['name'],
                        'content': java_content
                    })
                    
                    st.success(f"🎉 파일이 성공적으로 생성되었습니다!")
                    st.info(f"📁 생성된 경로: {project_folder}")
                    st.info(f"📄 생성된 파일: {file_info['name']}")
                
                # ZIP 파일 생성
                project_root = os.path.join(target_folder, file_list[0]['path'].split('/')[0]) if file_list else None
                if project_root and os.path.exists(project_root):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for root, dirs, files in os.walk(project_root):
                            for file in files:
                                file_path = os.path.join(root, file)
                                # ZIP 내부 경로 설정 (target 폴더 제외)
                                arcname = os.path.relpath(file_path, target_folder)
                                zip_file.write(file_path, arcname)
                    
                    zip_buffer.seek(0)
                    
                    # 세션 상태에 ZIP 데이터 저장
                    st.session_state.project_zip = {
                        'data': zip_buffer.getvalue(),
                        'filename': f"{config.get('project_name', 'project')}.zip"
                    }
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 프로젝트 생성 중 오류가 발생했습니다: {str(e)}")
    
    # 프로젝트 다운로드 섹션
    if 'project_zip' in st.session_state and st.session_state.project_zip:
        st.divider()
        st.subheader("📥 Download Generated Project")
        
        col_download1, col_download2, col_download3 = st.columns([1, 1, 1])
        
        with col_download2:
            # 프로젝트 ZIP 파일 다운로드 버튼
            st.download_button(
                label="� Download Project (ZIP)",
                data=st.session_state.project_zip['data'],
                file_name=st.session_state.project_zip['filename'],
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )


    
def main():
    """메인 애플리케이션"""
    # 페이지 설정
    st.set_page_config(
        page_title="Spring Boot Generator",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 세션 상태 초기화
    init_session_state()
    
    # 현재 페이지에 따라 렌더링
    if st.session_state.current_page == 'page1':
        render_page1()
    elif st.session_state.current_page == 'page2':
        render_page2()

if __name__ == "__main__":
    main()
