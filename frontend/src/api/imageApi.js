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
 * API Pipeline đầy đủ - Kết hợp cả Hiến và Hùng
 */
export const fullPipeline = async (
  imageBase64,
  smoothingMethod = 'bilateral',
  intensity = 'light',
  edgeMethod = 'canny',
  detailLevel = 'pencil',
  threshold1 = null,
  threshold2 = null,
  shadingIntensity = 0.5,
  edgeStrength = 0.4
) => {
  try {
    const body = {
      image: imageBase64,
      smoothing_method: smoothingMethod,
      intensity: intensity,
      edge_method: edgeMethod,
      detail_level: detailLevel,
      shading_intensity: shadingIntensity,
      edge_strength: edgeStrength,
    };
    
    if (threshold1 !== null && threshold1 !== undefined) {
      body.threshold1 = threshold1;
    }
    if (threshold2 !== null && threshold2 !== undefined) {
      body.threshold2 = threshold2;
    }
    
    const response = await fetch(`${API_BASE_URL}/full-pipeline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.message || 'Xử lý pipeline thất bại');
    }

    return data;
  } catch (error) {
    console.error('Error in full pipeline:', error);
    throw error;
  }
};

/**
 * API chuyển ảnh thành sketch/tranh vẽ tay (Người 2 - Hùng) - CHI TIẾT CAO
 */
export const sketchImage = async (
  imageBase64,
  smoothingMethod = 'bilateral',
  intensity = 'medium',
  edgeMethod = 'canny',
  detailLevel = 'medium',
  colored = false,  // Mặc định dùng tranh đen trắng
  colorPreservation = 0.7,
  threshold1 = null,
  threshold2 = null,
  shadingIntensity = 0.3,
  edgeStrength = 0.3
) => {
  try {
    const body = {
      image: imageBase64,
      smoothing_method: smoothingMethod,
      intensity: intensity,
      edge_method: edgeMethod,
      detail_level: detailLevel,
      colored: colored,
      color_preservation: colorPreservation,
      shading_intensity: shadingIntensity,
      edge_strength: edgeStrength,
    };
    
    // Chỉ thêm threshold nếu được chỉ định
    if (threshold1 !== null && threshold1 !== undefined) {
      body.threshold1 = threshold1;
    }
    if (threshold2 !== null && threshold2 !== undefined) {
      body.threshold2 = threshold2;
    }
    
    const response = await fetch(`${API_BASE_URL}/sketch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.message || 'Xử lý sketch thất bại');
    }

    return data;
  } catch (error) {
    console.error('Error creating sketch:', error);
    throw error;
  }
};

/**
 * API tạo hiệu ứng tranh vẽ có màu (Painting Effect)
 */
export const paintingImage = async (
  imageBase64,
  style = 'watercolor',
  intensity = 'medium',
  advanced = false
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/painting`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageBase64,
        style: style,
        intensity: intensity,
        advanced: advanced,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.message || 'Xử lý tranh vẽ thất bại');
    }

    return data;
  } catch (error) {
    console.error('Error creating painting:', error);
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
