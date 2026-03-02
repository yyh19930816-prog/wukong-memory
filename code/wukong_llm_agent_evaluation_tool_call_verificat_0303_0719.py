"""
RagaAI Catalyst Python Client Implementation
学习来源: GitHub raga-ai-hub/RagaAI-Catalyst
日期: 2023-11-15
功能描述: 实现RagaAI Catalyst的核心功能，包括项目管理和数据集管理
"""

from ragaai_catalyst import RagaAICatalyst, Dataset
import os

class RagaAIClient:
    def __init__(self, access_key=None, secret_key=None, base_url=None):
        """
        初始化RagaAI Catalyst客户端
        参数可以从环境变量获取或直接传入
        """
        self.access_key = access_key or os.getenv('RAGA_ACCESS_KEY')
        self.secret_key = secret_key or os.getenv('RAGA_SECRET_KEY')
        self.base_url = base_url or os.getenv('RAGA_BASE_URL')
        
        if not all([self.access_key, self.secret_key, self.base_url]):
            raise ValueError("Missing authentication credentials")
            
        self.client = RagaAICatalyst(
            access_key=self.access_key,
            secret_key=self.secret_key,
            base_url=self.base_url
        )

    def create_project(self, name, usecase):
        """
        创建新项目
        :param name: 项目名称
        :param usecase: 用例类型
        """
        return self.client.create_project(
            project_name=name,
            usecase=usecase
        )

    def list_projects(self):
        """列出所有项目"""
        return self.client.list_projects()

    def get_use_cases(self):
        """获取支持的用例类型"""
        return self.client.project_use_cases()

    def create_dataset(self, project_name, csv_path, dataset_name, schema_mapping):
        """
        从CSV创建数据集
        :param project_name: 所属项目名称
        :param csv_path: CSV文件路径
        :param dataset_name: 数据集名称
        :param schema_mapping: 列映射关系
        """
        dataset_manager = Dataset(project_name=project_name)
        return dataset_manager.create_from_csv(
            csv_path=csv_path,
            dataset_name=dataset_name,
            schema_mapping=schema_mapping
        )

    def list_datasets(self, project_name):
        """
        列出项目中的所有数据集
        :param project_name: 项目名称
        """
        dataset_manager = Dataset(project_name=project_name)
        return dataset_manager.list_datasets()


if __name__ == "__main__":
    # 示例用法 - 需要替换为您自己的凭据和测试数据
    try:
        # 初始化客户端
        raga_client = RagaAIClient(
            access_key="your_access_key",
            secret_key="your_secret_key",
            base_url="https://api.raga.ai"
        )

        # 项目操作示例
        print("支持的用例类型:", raga_client.get_use_cases())
        
        # 创建测试项目
        new_project = raga_client.create_project("Test-RAG-App", "Chatbot")
        print("创建的项目:", new_project)

        # 列出所有项目
        projects = raga_client.list_projects()
        print("所有项目:", projects)

        # 数据集操作示例 (需要实际CSV文件)
        # schema_map = {"question": "text", "answer": "text"}
        # dataset = raga_client.create_dataset(
        #     "Test-RAG-App",
        #     "test_data.csv",
        #     "test_dataset",
        #     schema_map
        # )
        # print("创建的数据集:", dataset)

    except Exception as e:
        print(f"发生错误: {str(e)}")