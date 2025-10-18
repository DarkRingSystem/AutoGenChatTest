

class PromptBuilder:
    """提示词构建器类"""

    def build_dynamic_prompt(self, template: str, **kwargs) -> str:
        """
        构建动态提示词
        
        参数:
            template: 提示词模板，包含 {变量名} 占位符
            **kwargs: 动态参数，键名对应模板中的占位符
            
        返回:
            替换后的完整提示词
            
        示例:
            template = "你是{role}，当前任务是{task}"
            prompt = builder.build_dynamic_prompt(template, role="专家", task="代码分析")
        """
        prompt = template
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        return prompt

    @staticmethod
    def create_system_prompt(template: str, **kwargs) -> str:
        """
        静态方法：快速创建系统提示词
        
        参数:
            template: 提示词模板
            **kwargs: 动态参数
            
        返回:
            完整的系统提示词
        """
        prompt = template
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        return prompt

    def create_normal_chat_prompt(template: str, **kwargs) -> str:
        """
        创建普通对话的系统提示词
        
        参数:
            template: 提示词模板
            **kwargs: 动态参数
            
        返回:
            完整的系统提示词
        """
        user_context = kwargs.get("user_context", "中文回复")

        template = """
        你是一个智能助手，可以回答各种问题并提供帮助。请用清晰、准确、友好的方式回答用户的问题。        
        用户要求：{user_context}
        """
        prompt = template
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        return prompt