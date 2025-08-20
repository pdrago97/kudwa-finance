'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Upload, 
  FileText, 
  Image, 
  File,
  CheckCircle,
  Clock,
  AlertCircle,
  X,
  Download
} from 'lucide-react'

interface UploadedFile {
  id: string
  name: string
  size: string
  type: string
  status: 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
}

export default function UploadPage() {
  const [files, setFiles] = useState<UploadedFile[]>([
    {
      id: '1',
      name: 'financial_report_q3.pdf',
      size: '2.4 MB',
      type: 'PDF',
      status: 'completed',
      progress: 100
    },
    {
      id: '2',
      name: 'transaction_data.csv',
      size: '1.8 MB',
      type: 'CSV',
      status: 'processing',
      progress: 65
    }
  ])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = event.target.files
    if (uploadedFiles) {
      Array.from(uploadedFiles).forEach((file) => {
        const newFile: UploadedFile = {
          id: Date.now().toString() + Math.random(),
          name: file.name,
          size: `${(file.size / 1024 / 1024).toFixed(1)} MB`,
          type: file.name.split('.').pop()?.toUpperCase() || 'FILE',
          status: 'uploading',
          progress: 0
        }
        
        setFiles(prev => [...prev, newFile])
        
        // Simulate upload progress
        const interval = setInterval(() => {
          setFiles(prev => prev.map(f => {
            if (f.id === newFile.id) {
              const newProgress = Math.min(f.progress + Math.random() * 20, 100)
              return {
                ...f,
                progress: newProgress,
                status: newProgress === 100 ? 'completed' : 'uploading'
              }
            }
            return f
          }))
        }, 500)
        
        setTimeout(() => clearInterval(interval), 5000)
      })
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'processing':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-red-500" />
      case 'jpg':
      case 'jpeg':
      case 'png':
        return <Image className="h-5 w-5 text-green-500" />
      default:
        return <File className="h-5 w-5 text-blue-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Document Upload</h1>
          <p className="text-muted-foreground">
            Upload and process documents for ontology extension and data ingestion
          </p>
        </div>
        <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-100 dark:bg-green-900 dark:text-green-100">
          <Upload className="mr-1 h-3 w-3" />
          Ready
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Drop Zone */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Files</CardTitle>
              <CardDescription>
                Drag and drop files or click to browse. Supports PDF, CSV, Excel, and image files.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center hover:border-muted-foreground/50 transition-colors">
                <div className="space-y-4">
                  <div className="flex justify-center">
                    <div className="h-16 w-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                      <Upload className="h-8 w-8 text-white" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">Drop files here</h3>
                    <p className="text-sm text-muted-foreground">
                      or click to browse your computer
                    </p>
                  </div>
                  <div>
                    <input
                      type="file"
                      multiple
                      onChange={handleFileUpload}
                      className="hidden"
                      id="file-upload"
                      accept=".pdf,.csv,.xlsx,.xls,.jpg,.jpeg,.png,.txt"
                    />
                    <label htmlFor="file-upload">
                      <Button asChild>
                        <span>Choose Files</span>
                      </Button>
                    </label>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Maximum file size: 10MB per file
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* File List */}
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Files</CardTitle>
              <CardDescription>
                Track the progress of your uploaded documents
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {files.map((file) => (
                  <div key={file.id} className="flex items-center space-x-4 p-3 border rounded-lg">
                    <div className="flex-shrink-0">
                      {getFileIcon(file.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium truncate">{file.name}</p>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(file.status)}
                          <Button variant="ghost" size="sm">
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <p className="text-xs text-muted-foreground">
                          {file.size} • {file.type}
                        </p>
                        <Badge variant="secondary" className="text-xs">
                          {file.status}
                        </Badge>
                      </div>
                      {file.status === 'uploading' || file.status === 'processing' ? (
                        <Progress value={file.progress} className="mt-2" />
                      ) : null}
                    </div>
                  </div>
                ))}
                {files.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No files uploaded yet
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Upload Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Upload Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Files</span>
                <span className="font-medium">{files.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Completed</span>
                <span className="font-medium text-green-600">
                  {files.filter(f => f.status === 'completed').length}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Processing</span>
                <span className="font-medium text-blue-600">
                  {files.filter(f => f.status === 'processing').length}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Supported Formats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Supported Formats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4 text-red-500" />
                <span className="text-sm">PDF Documents</span>
              </div>
              <div className="flex items-center space-x-2">
                <File className="h-4 w-4 text-green-500" />
                <span className="text-sm">CSV, Excel Files</span>
              </div>
              <div className="flex items-center space-x-2">
                <Image className="h-4 w-4 text-blue-500" />
                <span className="text-sm">Images (JPG, PNG)</span>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Download className="mr-2 h-4 w-4" />
                Export Results
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <FileText className="mr-2 h-4 w-4" />
                View Logs
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
