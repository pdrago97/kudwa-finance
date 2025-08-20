'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  Database, 
  Search, 
  Plus, 
  Edit,
  Trash2,
  Building2,
  Users,
  CreditCard,
  Filter
} from 'lucide-react'

const entities = [
  {
    id: '1',
    type: 'Company',
    name: 'Acme Corp',
    properties: { industry: 'Technology', employees: '500+' },
    lastUpdated: '2024-01-15'
  },
  {
    id: '2',
    type: 'Person',
    name: 'John Doe',
    properties: { role: 'CEO', company: 'Acme Corp' },
    lastUpdated: '2024-01-14'
  },
  {
    id: '3',
    type: 'Transaction',
    name: 'Payment #12345',
    properties: { amount: '$50,000', status: 'Completed' },
    lastUpdated: '2024-01-13'
  }
]

export default function DataPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Management</h1>
          <p className="text-muted-foreground">
            Entity and instance management for your ontology
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Entity
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Entities</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,247</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+23</span> added this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Entity Types</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">42</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-blue-600">3</span> new types this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Relationships</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3,891</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-purple-600">+156</span> new connections
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search entities..." className="pl-10" />
          </div>
        </div>
        <Button variant="outline">
          <Filter className="mr-2 h-4 w-4" />
          Filter by Type
        </Button>
      </div>

      {/* Entity List */}
      <Card>
        <CardHeader>
          <CardTitle>Entities</CardTitle>
          <CardDescription>
            Manage your ontology entities and their properties
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {entities.map((entity) => (
              <div key={entity.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                      {entity.type === 'Company' && <Building2 className="h-5 w-5 text-white" />}
                      {entity.type === 'Person' && <Users className="h-5 w-5 text-white" />}
                      {entity.type === 'Transaction' && <CreditCard className="h-5 w-5 text-white" />}
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium">{entity.name}</h3>
                      <Badge variant="secondary">{entity.type}</Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {Object.entries(entity.properties).map(([key, value]) => (
                        <span key={key} className="mr-4">
                          {key}: {value}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Last updated: {entity.lastUpdated}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4" />
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
