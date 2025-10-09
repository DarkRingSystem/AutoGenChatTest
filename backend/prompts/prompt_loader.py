"""
提示词加载器模块
负责从文件中加载智能体的系统提示词
"""
import os
from pathlib import Path
from typing import Dict, Optional


class PromptLoader:
    """提示词加载器类"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化提示词加载器
        
        参数:
            prompts_dir: 提示词文件目录，默认为当前文件所在目录
        """
        if prompts_dir is None:
            # 默认使用当前文件所在目录
            self.prompts_dir = Path(__file__).parent
        else:
            self.prompts_dir = Path(prompts_dir)
        
        # 缓存已加载的提示词
        self._cache: Dict[str, str] = {}
    
    def load(self, prompt_name: str, use_cache: bool = True) -> str:
        """
        加载指定的提示词
        
        参数:
            prompt_name: 提示词名称（不含扩展名）
            use_cache: 是否使用缓存
            
        返回:
            提示词内容
            
        异常:
            FileNotFoundError: 提示词文件不存在
        """
        # 检查缓存
        if use_cache and prompt_name in self._cache:
            return self._cache[prompt_name]
        
        # 构建文件路径
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        # 检查文件是否存在
        if not prompt_file.exists():
            raise FileNotFoundError(
                f"提示词文件不存在: {prompt_file}\n"
                f"请确保文件 '{prompt_name}.txt' 存在于 {self.prompts_dir} 目录中"
            )
        
        # 读取文件内容
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 缓存内容
            if use_cache:
                self._cache[prompt_name] = content
            
            return content
            
        except Exception as e:
            raise RuntimeError(f"读取提示词文件失败: {prompt_file}, 错误: {e}")
    
    def reload(self, prompt_name: str) -> str:
        """
        重新加载指定的提示词（忽略缓存）
        
        参数:
            prompt_name: 提示词名称
            
        返回:
            提示词内容
        """
        # 清除缓存
        if prompt_name in self._cache:
            del self._cache[prompt_name]
        
        # 重新加载
        return self.load(prompt_name, use_cache=True)
    
    def clear_cache(self):
        """清除所有缓存"""
        self._cache.clear()
    
    def list_prompts(self) -> list[str]:
        """
        列出所有可用的提示词
        
        返回:
            提示词名称列表
        """
        if not self.prompts_dir.exists():
            return []
        
        prompts = []
        for file in self.prompts_dir.glob("*.txt"):
            prompts.append(file.stem)
        
        return sorted(prompts)
    
    def get_prompt_path(self, prompt_name: str) -> Path:
        """
        获取提示词文件的完整路径
        
        参数:
            prompt_name: 提示词名称
            
        返回:
            文件路径
        """
        return self.prompts_dir / f"{prompt_name}.txt"


# 创建全局提示词加载器实例
_global_loader: Optional[PromptLoader] = None


def get_prompt_loader() -> PromptLoader:
    """
    获取全局提示词加载器实例
    
    返回:
        PromptLoader 实例
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = PromptLoader()
    return _global_loader


def load_prompt(prompt_name: str) -> str:
    """
    便捷函数：加载指定的提示词
    
    参数:
        prompt_name: 提示词名称
        
    返回:
        提示词内容
    """
    return get_prompt_loader().load(prompt_name)


# 预定义的提示词名称常量
class PromptNames:
    """提示词名称常量"""
    # 通用助手
    ASSISTANT = "assistant"

    # 测试用例团队
    TEST_CASE_GENERATOR = "test_case_generator"
    TEST_CASE_REVIEWER = "test_case_reviewer"
    TEST_CASE_OPTIMIZER = "test_case_optimizer"

    # UI 图像分析团队
    UI_EXPERT = "ui_expert"
    INTERACTION_ANALYST = "interaction_analyst"
    TEST_SCENARIO_EXPERT = "test_scenario_expert"

