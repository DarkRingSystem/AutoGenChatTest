/**
 * API 服务层
 * 统一管理所有 API 调用
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * 普通对话 API
 */
export const chatNormalAPI = {
  /**
   * 流式对话
   */
  async stream(message, conversationId, fileIds = []) {
    const response = await fetch(`${API_BASE_URL}/api/chat/normal/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        file_ids: fileIds.length > 0 ? fileIds : undefined,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  },

  /**
   * 非流式对话
   */
  async chat(message, conversationId, fileIds = []) {
    const response = await fetch(`${API_BASE_URL}/api/chat/normal/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        file_ids: fileIds.length > 0 ? fileIds : undefined,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
};

/**
 * 测试用例生成 API
 */
export const chatTestcaseAPI = {
  /**
   * 流式生成测试用例
   */
  async stream(message, conversationId, isFeedback = false, targetAgent = null, fileIds = []) {
    const response = await fetch(`${API_BASE_URL}/api/chat/testcase/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        is_feedback: isFeedback,
        target_agent: targetAgent,
        file_ids: fileIds.length > 0 ? fileIds : undefined,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  },
};

/**
 * 图片分析 API
 */
export const imageAnalysisAPI = {
  /**
   * 流式图片分析
   */
  async stream(imageFile, prompt = '分析这张 UI 界面图片，生成详细的测试用例') {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('prompt', prompt);

    const response = await fetch(`${API_BASE_URL}/api/image-analysis/stream`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  },

  /**
   * 非流式图片分析
   */
  async analyze(imageFile, prompt = '分析这张 UI 界面图片，生成详细的测试用例') {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('prompt', prompt);

    const response = await fetch(`${API_BASE_URL}/api/image-analysis/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
};

/**
 * 文件管理 API
 */
export const filesAPI = {
  /**
   * 批量解析文件
   */
  async parse(files) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await fetch(`${API_BASE_URL}/api/files/parse`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * 单文件转换
   */
  async convert(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/files/convert`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * 获取文件内容
   */
  async getContent(fileId) {
    const response = await fetch(`${API_BASE_URL}/api/files/storage/${fileId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * 删除文件
   */
  async delete(fileId) {
    const response = await fetch(`${API_BASE_URL}/api/files/storage/${fileId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * 列出所有文件
   */
  async list() {
    const response = await fetch(`${API_BASE_URL}/api/files/storage`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * 清除所有文件
   */
  async clearAll() {
    const response = await fetch(`${API_BASE_URL}/api/files/storage`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
};

/**
 * 首页 API
 */
export const homeAPI = {
  /**
   * 获取首页信息
   */
  async getInfo() {
    const response = await fetch(`${API_BASE_URL}/api/home/`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * 获取统计信息
   */
  async getStats() {
    const response = await fetch(`${API_BASE_URL}/api/home/stats`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
};

/**
 * 健康检查 API
 */
export const healthAPI = {
  async check() {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
};

