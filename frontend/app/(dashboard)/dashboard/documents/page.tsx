'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  FileText, 
  Search, 
  Filter, 
  Download,
  Eye,
  Trash2,
  Calendar,
  User,
  File
} from 'lucide-react'

const documents = [
  {
    id: '1',
    name: 'Q3 Financial Report.pdf',
    type: 'PDF',
    size: '2.4 MB',
    uploadedBy: 'John Doe',
    uploadedAt: '2024-01-15',
    status: 'processed'
  },
  {
    id: '2',
    name: 'Transaction Data.csv',
    type: 'CSV',
    size: '1.8 MB',
    uploadedBy: 'Jane Smith',
    uploadedAt: '2024-01-14',
    status: 'processing'
  },
  {
    id: '3',
    name: 'Company Contracts.xlsx',
    type: 'Excel',
    size: '3.2 MB',
    uploadedBy: 'Mike Johnson',
    uploadedAt: '2024-01-13',
    status: 'processed'
  }
]

export default function DocumentsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground">
            Manage and organize your uploaded documents
          </p>
        </div>
        <Button>
          <FileText className="mr-2 h-4 w-4" />
          Upload Document
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search documents..." className="pl-10" />
          </div>
        </div>
        <Button variant="outline">
          <Filter className="mr-2 h-4 w-4" />
          Filter
        </Button>
      </div>

      {/* Documents Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Documents</CardTitle>
          <CardDescription>
            {documents.length} documents uploaded
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                      <File className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium">{doc.name}</h3>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <span>{doc.type} • {doc.size}</span>
                      <div className="flex items-center space-x-1">
                        <User className="h-3 w-3" />
                        <span>{doc.uploadedBy}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-3 w-3" />
                        <span>{doc.uploadedAt}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={doc.status === 'processed' ? 'default' : 'secondary'}>
                    {doc.status}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
