'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { KnowledgeGraph } from '@/components/knowledge-graph/knowledge-graph'
import { ontologyService } from '@/lib/supabase'
import {
  Network,
  Zap,
  Database,
  Users,
  Building2,
  TrendingUp,
  Search,
  Filter,
  Maximize2,
  RefreshCw,
  Trash2
} from 'lucide-react'

export default function GraphPage() {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [stats, setStats] = useState({ entities: 0, relations: 0 })
  const [entityTypes, setEntityTypes] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)

  // Load real statistics from Supabase
  useEffect(() => {
    const loadStats = async () => {
      try {
        setLoading(true)
        const [statsData, { entities }] = await Promise.all([
          ontologyService.getStats(),
          ontologyService.getGraphData()
        ])

        setStats(statsData)

        // Count entity types
        const typeCounts: Record<string, number> = {}
        entities.forEach(entity => {
          const type = entity.name || 'Unknown'
          typeCounts[type] = (typeCounts[type] || 0) + 1
        })
        setEntityTypes(typeCounts)
      } catch (error) {
        console.error('Error loading stats:', error)
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [])

  const handleResetData = async () => {
    if (confirm('Are you sure you want to reset all data? This action cannot be undone.')) {
      try {
        const response = await fetch('/api/reset-data', { method: 'POST' })
        const result = await response.json()

        if (result.success) {
          alert('All data has been reset successfully!')
          // Refresh the stats after reset
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Graph</h1>
          <p className="text-muted-foreground">
            Interactive ontology visualization with GraphRAG capabilities
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="default" className="bg-purple-100 text-purple-800 hover:bg-purple-100 dark:bg-purple-900 dark:text-purple-100">
            <Network className="mr-1 h-3 w-3" />
            Connected
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            <Maximize2 className="mr-2 h-4 w-4" />
            Fullscreen
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={handleResetData}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Reset All Data
          </Button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center space-x-4">
        <Button variant="outline" size="sm">
          <Search className="mr-2 h-4 w-4" />
          Search Nodes
        </Button>
        <Button variant="outline" size="sm">
          <Filter className="mr-2 h-4 w-4" />
          Filter
        </Button>
        <Button variant="outline" size="sm">
          <TrendingUp className="mr-2 h-4 w-4" />
          Analytics
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Graph Visualization */}
        <div className="lg:col-span-3">
          <Card className="h-[600px]">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Network className="mr-2 h-5 w-5" />
                Ontology Graph
              </CardTitle>
              <CardDescription>
                Interactive visualization of entities, relationships, and data flows
              </CardDescription>
            </CardHeader>
            <CardContent className="h-full p-0">
              <div className="h-full rounded-lg overflow-hidden">
                <KnowledgeGraph onResetData={handleResetData} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Graph Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Graph Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="h-3 w-3 rounded-full bg-blue-500"></div>
                  <span className="text-sm text-muted-foreground">Entities</span>
                </div>
                <span className="font-medium">
                  {loading ? '...' : stats.entities.toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="h-3 w-3 rounded-full bg-green-500"></div>
                  <span className="text-sm text-muted-foreground">Relations</span>
                </div>
                <span className="font-medium">
                  {loading ? '...' : stats.relations.toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="h-3 w-3 rounded-full bg-purple-500"></div>
                  <span className="text-sm text-muted-foreground">Types</span>
                </div>
                <span className="font-medium">
                  {loading ? '...' : Object.keys(entityTypes).length}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Entity Types */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Entity Types</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {loading ? (
                <div className="text-center text-sm text-muted-foreground">Loading...</div>
              ) : Object.keys(entityTypes).length === 0 ? (
                <div className="text-center text-sm text-muted-foreground">No entity types found</div>
              ) : (
                Object.entries(entityTypes).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {type.toLowerCase().includes('report') && <Database className="h-4 w-4 text-blue-500" />}
                      {type.toLowerCase().includes('account') && <Building2 className="h-4 w-4 text-green-500" />}
                      {type.toLowerCase().includes('period') && <TrendingUp className="h-4 w-4 text-purple-500" />}
                      {type.toLowerCase().includes('observation') && <Zap className="h-4 w-4 text-orange-500" />}
                      {!type.toLowerCase().includes('report') &&
                       !type.toLowerCase().includes('account') &&
                       !type.toLowerCase().includes('period') &&
                       !type.toLowerCase().includes('observation') &&
                       <Database className="h-4 w-4 text-gray-500" />}
                      <span className="text-sm">{type}</span>
                    </div>
                    <Badge variant="secondary">{count}</Badge>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Search className="mr-2 h-4 w-4" />
                Find Entity
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <TrendingUp className="mr-2 h-4 w-4" />
                Path Analysis
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Network className="mr-2 h-4 w-4" />
                Cluster View
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
