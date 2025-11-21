/**
 * API client cho backend Drawify
 */

const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Chuyển file thành base64 string
 */
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};

/**
 * API Preprocessing: Grayscale + Smoothing (Người 1 - Hiến)
 */
export const preprocessImage = async (imageBase64, method = 'bilateral', intensity = 'medium') => {
  try {
    const response = await fetch(`${API_BASE_URL}/preprocess`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageBase64,
        method: method,
        intensity: intensity,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'Xử lý ảnh thất bại');
    }

    return data;
  } catch (error) {
    console.error('Error preprocessing image:', error);
    throw error;
  }
};

/**
 * API chỉ chuyển xám (để test)
 */
export const grayscaleOnly = async (imageBase64) => {
  try {
    const response = await fetch(`${API_BASE_URL}/grayscale`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageBase64,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'Chuyển xám thất bại');
    }

    return data;
  } catch (error) {
    console.error('Error converting to grayscale:', error);
    throw error;
  }
};

/**
 * Download ảnh từ base64
 */
export const downloadImage = (base64String, filename = 'processed_image.png') => {
  const link = document.createElement('a');
  link.href = base64String;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Kiểm tra server có hoạt động không
 */
export const checkServerHealth = async () => {
  try {
    const response = await fetch('http://localhost:5000/health');
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Server health check failed:', error);
    return false;
  }
};
