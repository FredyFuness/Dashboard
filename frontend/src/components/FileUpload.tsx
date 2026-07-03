import { useRef, useState } from 'react'

interface Props {
  onFileSelected: (file: File) => void
  disabled?: boolean
}

const ACCEPTED = '.xlsx,.xls,.xlsm'

export default function FileUpload({ onFileSelected, disabled }: Props) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFiles = (files: FileList | null) => {
    const file = files?.[0]
    if (file) onFileSelected(file)
  }

  return (
    <div
      className={`upload-zone${isDragging ? ' dragging' : ''}${disabled ? ' disabled' : ''}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault()
        if (!disabled) setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setIsDragging(false)
        if (!disabled) handleFiles(e.dataTransfer.files)
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        hidden
        disabled={disabled}
        onChange={(e) => handleFiles(e.target.files)}
      />
      <p className="upload-title">Arrastrá tu archivo Excel aquí</p>
      <p className="upload-subtitle">o hacé clic para elegirlo (.xlsx, .xls, .xlsm)</p>
    </div>
  )
}
