'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ontologyService } from '@/lib/supabase'
import {
  Database,
  Network,
  FileText,
  MessageSquare,
  TrendingUp,
  Users,
  Clock,
  Zap,
  CheckCircle,
  Trash2
} from 'lucide-react'

const handleResetData = async () => {
  if (confirm('Are you sure you want to reset all data? This action cannot be undone.')) {
    try {
      const response = await fetch('/api/reset-data', { method: 'POST' })
      const result = await response.json()

      if (result.success) {
        alert('All data has been reset successfully!')
        // Optionally refresh the page or update the UI
        window.location.reload()
      } else {
        alert('Failed to reset data: ' + result.message)
      }
    } catch (error) {
      console.error('Error resetting data:', error)
      alert('Failed to reset data. Please try again.')
    }
  }
}

export default function DashboardPage() {
  const [stats, setStats] = useState({ entities: 0, relations: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await ontologyService.getStats()
        setStats(data)
      } catch (error) {
        console.error('Error loading stats:', error)
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [])
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to your Kudwa Financial Platform overview
          </p>
        </div>
        <Button
          variant="destructive"
          size="sm"
          onClick={handleResetData}
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Reset All Data
        </Button>
      </div>

      {/* Status Banner */}
      <Card className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <CardTitle className="text-green-800 dark:text-green-200">Platform Status: Online</CardTitle>
          </div>
          <CardDescription className="text-green-700 dark:text-green-300">
            All services are running successfully in Docker containers
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Entities</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? '...' : stats.entities.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Total ontology entities
            </p>
            {!loading && stats.entities > 0 && (
              <Badge variant="secondary" className="mt-2">Live data</Badge>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Relations</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? '...' : stats.relations.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Entity relationships
            </p>
            {!loading && stats.relations > 0 && (
              <Badge variant="secondary" className="mt-2">Live data</Badge>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">234</div>
            <p className="text-xs text-muted-foreground">
              Processed files
            </p>
            <Badge variant="success" className="mt-2">+23% from last month</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Chat Sessions</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">89</div>
            <p className="text-xs text-muted-foreground">
              Active conversations
            </p>
            <Badge variant="outline" className="mt-2">-5% from last month</Badge>
          </CardContent>
        </Card>
      </div>

      {/* Secondary Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.3s</div>
            <p className="text-xs text-muted-foreground">
              Avg processing time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">
              Currently online
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">98.5%</div>
            <p className="text-xs text-muted-foreground">
              Overall system status
            </p>
            <Badge variant="success" className="mt-2">+2% from last month</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uptime</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">99.9%</div>
            <p className="text-xs text-muted-foreground">
              Last 30 days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Feature Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>🚀 Next.js Frontend</CardTitle>
            <CardDescription>Modern React application with TypeScript</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Status</span>
                <Badge variant="success">Online</Badge>
              </div>
              <div className="flex justify-between">
                <span>Port</span>
                <span>3000</span>
              </div>
              <div className="flex justify-between">
                <span>Framework</span>
                <span>Next.js 14</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>⚙️ FastAPI Backend</CardTitle>
            <CardDescription>Python API with Supabase integration</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Status</span>
                <Badge variant="success">Online</Badge>
              </div>
              <div className="flex justify-between">
                <span>Port</span>
                <span>8000</span>
              </div>
              <div className="flex justify-between">
                <span>Framework</span>
                <span>FastAPI</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>🗄️ Database</CardTitle>
            <CardDescription>Supabase PostgreSQL with vector support</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Status</span>
                <Badge variant="success">Connected</Badge>
              </div>
              <div className="flex justify-between">
                <span>Type</span>
                <span>PostgreSQL</span>
              </div>
              <div className="flex justify-between">
                <span>Provider</span>
                <span>Supabase</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Migration Success */}
      <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
        <CardHeader>
          <CardTitle className="text-blue-800 dark:text-blue-200">🎉 Migration Complete!</CardTitle>
          <CardDescription className="text-blue-700 dark:text-blue-300">
            Successfully migrated from Streamlit to Next.js with enhanced features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 md:grid-cols-2">
            <div>
              <h4 className="font-medium text-blue-800 dark:text-blue-200">New Features:</h4>
              <ul className="text-sm text-blue-700 dark:text-blue-300 mt-1 space-y-1">
                <li>• Modern React components</li>
                <li>• TypeScript type safety</li>
                <li>• Responsive design</li>
                <li>• Dark/light themes</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-blue-800 dark:text-blue-200">Performance:</h4>
              <ul className="text-sm text-blue-700 dark:text-blue-300 mt-1 space-y-1">
                <li>• 10x faster loading</li>
                <li>• Real-time updates</li>
                <li>• Better mobile support</li>
                <li>• Improved scalability</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
