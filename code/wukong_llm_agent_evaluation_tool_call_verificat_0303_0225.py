"""
RagaAI Catalyst Integration Script
学习来源: https://github.com/raga-ai-hub/RagaAI-Catalyst
日期: 当前日期
功能: 演示核心功能包括项目管理、数据集管理和模型评估
注意: 需先安装ragaai-catalyst包并配置认证信息
"""

from ragaai_catalyst import RagaAICatalyst, Dataset
import os

# 配置认证信息 - 从环境变量获取或直接填写
ACCESS_KEY = os.getenv('RAGA_ACCESS_KEY', 'your_access_key')
SECRET_KEY = os.getenv('RAGA_SECRET_KEY', 'your_secret_key')
BASE_URL = os.getenv('RAGA_BASE_URL', 'https://api.raga.ai')

def initialize_client():
    """初始化RagaAI客户端"""
    try:
        catalyst = RagaAICatalyst(
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            base_url=BASE_URL
        )
        print("✅ RagaAI客户端初始化成功")
        return catalyst
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return None

def project_management_demo(catalyst):
    """演示项目管理功能"""
    print("\n=== 项目管理演示 ===")
    
    # 创建新项目
    try:
        project = catalyst.create_project(
            project_name="Demo-RAG-App",
            usecase="Information Retrieval"
        )
        print(f"创建项目成功: {project['name']}")
    except Exception as e:
        print(f"创建项目失败: {str(e)}")
    
    # 列出所有项目
    try:
        projects = catalyst.list_projects()
        print("\n现有项目列表:")
        for idx, proj in enumerate(projects, 1):
            print(f"{idx}. {proj['name']} - 用例: {proj['usecase']}")
    except Exception as e:
        print(f"获取项目列表失败: {str(e)}")

def dataset_management_demo(catalyst, project_name):
    """演示数据集管理功能"""
    print("\n=== 数据集管理演示 ===")
    
    dataset_manager = Dataset(
        project_name=project_name,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        base_url=BASE_URL
    )
    
    # 列出数据集
    try:
        datasets = dataset_manager.list_datasets()
        print("现有数据集:")
        for ds in datasets:
            print(f"- {ds['name']} (创建于: {ds['created_at']})")
    except Exception as e:
        print(f"获取数据集列表失败: {str(e)}")

def main():
    # 初始化客户端
    catalyst = initialize_client()
    if not catalyst:
        return
    
    # 演示核心功能
    project_management_demo(catalyst)
    
    # 使用已存在的项目名进行数据集演示
    dataset_management_demo(catalyst, "Demo-RAG-App")
    
    print("\n✨ 演示完成")

if __name__ == "__main__":
    main()