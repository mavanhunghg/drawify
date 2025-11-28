import { useState, useEffect } from 'react'
import './App.css'
import { fileToBase64, downloadImage, checkServerHealth, fullPipeline } from './api/imageApi'

function App() {
  const [originalImage, setOriginalImage] = useState(null)
  const [processedImage, setProcessedImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [method, setMethod] = useState('bilateral')
  const [serverOnline, setServerOnline] = useState(false)
  const [processingInfo, setProcessingInfo] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [edgeMethod, setEdgeMethod] = useState('canny')
  const [cannyThreshold, setCannyThreshold] = useState(50)
  
  // Cố định các giá trị
  const mode = 'full'
  const intensity = 'light'
  const detailLevel = 'pencil'
  const invertColors = false

  // Kiểm tra server khi load trang
  useEffect(() => {
    checkServerHealth().then(setServerOnline)
    const interval = setInterval(() => {
      checkServerHealth().then(setServerOnline)
    }, 5000) // Check mỗi 5 giây
    return () => clearInterval(interval)
  }, [])

  // Hàm xử lý file
  const processImageFile = async (file) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setError('Vui lòng chọn file ảnh!')
      return
    }
    try {
      setError(null)
      const base64 = await fileToBase64(file)
      setOriginalImage(base64)
      setProcessedImage(null)
      setProcessingInfo(null)
    } catch (err) {
      setError('Không thể đọc file ảnh: ' + err.message)
    }
  }

  // Xử lý upload ảnh
  const handleImageUpload = async (event) => {
    const file = event.target.files[0]
    await processImageFile(file)
  }

  // Xử lý drag & drop
  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      await processImageFile(files[0])
    }
  }

  // Xử lý Full Pipeline 
  const handleFullPipeline = async () => {
    if (!originalImage) {
      setError('Vui lòng tải ảnh lên trước!')
      return
    }
    if (!serverOnline) {
      setError('Backend server chưa chạy! Vui lòng chạy: cd backend && python app.py')
      return
    }
    setLoading(true)
    setError(null)
    try {
      // Tự động tính high threshold = 3 × low threshold
      const lowThreshold = cannyThreshold
      const highThreshold = cannyThreshold * 3
      
      const result = await fullPipeline(
        originalImage,
        method,  // smoothing_method
        intensity,
        edgeMethod,
        detailLevel,
        lowThreshold,
        highThreshold,
        invertColors
      )
      setProcessedImage(result.image)
      setProcessingInfo({
        method: 'full-pipeline',
        smoothing_method: method,
        intensity: intensity,
        edge_method: edgeMethod,
        detail_level: detailLevel,
        message: result.message,
        shape: result.shape,
        steps: result.steps,
        pipeline: result.pipeline
      })
    } catch (err) {
      setError('Lỗi xử lý pipeline: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Download ảnh
  const handleDownload = () => {
    if (processedImage) {
      const filename = `preprocessed_${method}_${intensity}_${Date.now()}.png`
      downloadImage(processedImage, filename)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🎨 Drawify</h1>
        <div className={`server-status ${serverOnline ? 'online' : 'offline'}`}>
          {serverOnline ? (
            <>✅ Server đang chạy</>
          ) : (
            <>❌ Server offline - Chạy: cd backend && python app.py</>
          )}
        </div>
      </header>

      <main className="main">
        {/* Upload Section */}
        <section className="upload-section">
          <h2> Bước 1: Tải ảnh lên</h2>
          <div
            className={`drop-zone ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <p> Kéo thả ảnh vào đây</p>
            <p className="or-text">hoặc</p>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="file-input"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="file-label">
              Chọn ảnh từ máy
            </label>
          </div>


        </section>

        {/* Settings Section */}
        {originalImage && (
          <section className="settings-section">
            <h2>⚙️ Bước 2: Cấu hình xử lý</h2>

            <div className="setting-group">
              <label>Phương pháp làm mịn </label>
              <select value={method} onChange={(e) => setMethod(e.target.value)}>
                <option value="bilateral"> Bilateral Filter (Giữ biên )</option>
                <option value="gaussian">Gaussian Blur (Làm mịn đều)</option>
                <option value="median">Median Blur (Loại nhiễu)</option>
              </select>
            </div>

            <div className="setting-group">
              <label>Phương pháp phát hiện biên</label>
              <select value={edgeMethod} onChange={e => setEdgeMethod(e.target.value)}>
                <option value="canny"> Canny (Khuyên dùng )</option>
                <option value="sobel">Sobel (Gradient - Nhanh)</option>
                <option value="laplacian">Laplacian (Đạo hàm bậc 2)</option>
              </select>
            </div>

            {edgeMethod === 'canny' && (
              <div className="setting-group" style={{marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)'}}>
                <label>
                   Điều chỉnh độ nhạy Canny: {cannyThreshold}
                  <span style={{fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)', marginLeft: '0.5rem'}}>
                    (Tự động: Low={cannyThreshold}, High={cannyThreshold * 3})
                  </span>
                </label>
                <input
                  type="range"
                  min="20"
                  max="100"
                  value={cannyThreshold}
                  onChange={(e) => setCannyThreshold(parseInt(e.target.value))}
                  style={{width: '100%', cursor: 'pointer'}}
                />
                <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)'}}>
                  <span>20 (Nhạy - Nhiều nét, chi tiết)</span>
                  <span>100 (Ít nhạy - Ít nét, đơn giản)</span>
                </div>
                <div style={{fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginTop: '0.5rem', fontStyle: 'italic'}}>
                  💡 High threshold tự động = 3 × Low ({cannyThreshold} → {cannyThreshold * 3})
                </div>
              </div>
            )}


            <button
              onClick={handleFullPipeline}
              disabled={loading || !serverOnline}
              className="btn btn-primary"
              style={{fontSize: '1.1rem', padding: '1rem 2rem', marginTop: '1.5rem', width: '100%'}}
            >
              {loading ? (
                <> Đang xử lý Pipeline đầy đủ...</>
              ) : (
                <>Xử lý ảnh</>
              )}
            </button>
          </section>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {/* Processing Info */}
        {processingInfo && (
          <div className="info-message">
            ✅ {processingInfo.message}
            {processingInfo.shape && (
              <span> | Kích thước: {processingInfo.shape.join(' × ')} pixels</span>
            )}
            {processingInfo.method && processingInfo.method !== 'grayscale' && processingInfo.method !== 'sketch' && (
              <span> | Method: {processingInfo.method} | Intensity: {processingInfo.intensity}</span>
            )}
            {processingInfo.method === 'sketch' && (
              <span> | Edge: {processingInfo.edge_method} | Detail: {processingInfo.detail_level}</span>
            )}
            {processingInfo.method === 'full-pipeline' && (
              <>
                <span> | Smoothing: {processingInfo.smoothing_method} ({processingInfo.intensity})</span>
                <span> | Edge: {processingInfo.edge_method} | Detail: {processingInfo.detail_level}</span>
                {processingInfo.pipeline && (
                  <div style={{marginTop: '0.5rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)'}}>
                    📋 Pipeline: {processingInfo.pipeline.preprocessing.grayscale} → {processingInfo.pipeline.preprocessing.smoothing} → {processingInfo.pipeline.sketch.edge_detection} → {processingInfo.pipeline.sketch.sketch_effect}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Images Display */}
        {originalImage && (
          <section className="images-section">
            <h2> Bước 3: So sánh kết quả</h2>
            <div className="images-container">
              <div className="image-box">
                <h3>Ảnh gốc</h3>
                <img src={originalImage} alt="Original" className="image" />
              </div>
              <div className="image-box">
                <h3>
                  {mode === 'grayscale' 
                    ? 'Ảnh Grayscale'
                    : mode === 'sketch'
                    ? 'Ảnh Sketch (Edge Detection)'
                    : mode === 'full'
                    ? 'Ảnh Sketch cuối cùng (Pipeline đầy đủ)'
                    : 'Ảnh đã xử lý (Grayscale + Smoothing)'}
                </h3>
                {processedImage ? (
                  <>
                    <img src={processedImage} alt="Processed" className="image" />
                    <button onClick={handleDownload} className="btn btn-success">
                       Tải ảnh về
                    </button>
                  </>
                ) : (
                  <div className="placeholder">
                    <p>Chưa có ảnh xử lý</p>
                    <p> Nhấn nút xử lý ở trên</p>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

      </main>


    </div>
  )
}

export default App
