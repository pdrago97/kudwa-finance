'use client'

import React, { useCallback, useMemo, useState, useEffect } from 'react'
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ontologyService, OntologyEntity, OntologyRelation } from '@/lib/supabase'
import {
  Building2,
  Users,
  CreditCard,
  FileText,
  Zap,
  RefreshCw,
  Database,
  Calendar,
  TrendingUp,
  DollarSign
} from 'lucide-react'

// Helper function to convert Supabase entities to React Flow nodes
const convertEntitiesToNodes = (entities: OntologyEntity[]): Node[] => {
  return entities.map((entity, index) => {
    const nodeType = entity.name
    const color = getNodeColor(nodeType)

    return {
      id: entity.id,
      type: 'default',
      position: {
        x: (index % 4) * 200 + 100,
        y: Math.floor(index / 4) * 150 + 50
      },
      data: {
        label: entity.name,
        type: nodeType,
        properties: entity.properties || {}
      },
      style: {
        background: color.bg,
        color: 'white',
        border: `2px solid ${color.border}`,
        borderRadius: '8px',
        padding: '10px',
        fontSize: '12px',
        fontWeight: 'bold',
        minWidth: '120px',
        textAlign: 'center'
      }
    }
  })
}

// Helper function to convert Supabase relations to React Flow edges
const convertRelationsToEdges = (relations: OntologyRelation[]): Edge[] => {
  return relations.map((relation) => ({
    id: relation.id,
    source: relation.source_entity_id,
    target: relation.target_entity_id,
    label: relation.rel_type,
    type: 'smoothstep',
    style: { stroke: '#64748b', strokeWidth: 2 },
    labelStyle: { fontSize: '10px', fontWeight: 'bold' }
  }))
}

// Helper function to get node colors based on type
const getNodeColor = (type: string) => {
  switch (type.toLowerCase()) {
    case 'report':
      return { bg: '#3b82f6', border: '#1d4ed8' } // Blue
    case 'account':
      return { bg: '#10b981', border: '#059669' } // Green
    case 'period':
      return { bg: '#8b5cf6', border: '#7c3aed' } // Purple
    case 'observation':
      return { bg: '#f59e0b', border: '#d97706' } // Orange
    case 'company':
      return { bg: '#3b82f6', border: '#1d4ed8' } // Blue
    case 'person':
      return { bg: '#10b981', border: '#059669' } // Green
    case 'transaction':
      return { bg: '#8b5cf6', border: '#7c3aed' } // Purple
    case 'contract':
      return { bg: '#f59e0b', border: '#d97706' } // Orange
    default:
      return { bg: '#64748b', border: '#475569' } // Gray
  }
}

interface KnowledgeGraphProps {
  onResetData?: () => void
}

export function KnowledgeGraph({ onResetData }: KnowledgeGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load data from Supabase
  const loadGraphData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const { entities, relations } = await ontologyService.getGraphData()

      const newNodes = convertEntitiesToNodes(entities)
      const newEdges = convertRelationsToEdges(relations)

      setNodes(newNodes)
      setEdges(newEdges)
    } catch (err) {
      console.error('Error loading graph data:', err)
      setError('Failed to load graph data')
    } finally {
      setLoading(false)
    }
  }, [setNodes, setEdges])

  // Load data on component mount
  useEffect(() => {
    loadGraphData()
  }, [loadGraphData])

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])

  const resetGraph = useCallback(async () => {
    if (onResetData) {
      await onResetData()
    }
    // Reload data after reset
    await loadGraphData()
    setSelectedNode(null)
  }, [onResetData, loadGraphData])

  const nodeTypes = useMemo(() => ({}), [])

  const getNodeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'report':
        return <FileText className="h-4 w-4" />
      case 'account':
        return <Database className="h-4 w-4" />
      case 'period':
        return <Calendar className="h-4 w-4" />
      case 'observation':
        return <TrendingUp className="h-4 w-4" />
      case 'company':
        return <Building2 className="h-4 w-4" />
      case 'person':
        return <Users className="h-4 w-4" />
      case 'transaction':
        return <CreditCard className="h-4 w-4" />
      case 'contract':
        return <FileText className="h-4 w-4" />
      default:
        return <Zap className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <div className="h-full w-full flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading knowledge graph...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full w-full flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="text-red-500">
            <Zap className="h-12 w-12 mx-auto mb-2" />
          </div>
          <p className="text-red-600">{error}</p>
          <Button onClick={loadGraphData} variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Retry
          </Button>
        </div>
      </div>
    )
  }

  if (nodes.length === 0) {
    return (
      <div className="h-full w-full flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="text-muted-foreground">
            <Database className="h-12 w-12 mx-auto mb-2" />
          </div>
          <p className="text-muted-foreground">No entities found in the knowledge graph</p>
          <p className="text-sm text-muted-foreground">Upload some documents to populate the ontology</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        className="bg-background"
      >
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const color = getNodeColor(node.data.type)
            return color.bg
          }}
          className="!bg-background !border-border"
        />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>

      {/* Reset Button */}
      <div className="absolute top-4 right-4 z-10">
        <Button 
          onClick={resetGraph}
          variant="outline"
          size="sm"
          className="bg-background/80 backdrop-blur-sm"
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Reset Data
        </Button>
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 z-10 w-80">
          <Card className="bg-background/95 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center">
                  {getNodeIcon(selectedNode.data.type)}
                  <span className="ml-2">{selectedNode.data.label}</span>
                </CardTitle>
                <Badge variant="secondary">{selectedNode.data.type}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(selectedNode.data.properties || {}).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-muted-foreground capitalize">{key}:</span>
                    <span className="font-medium">{value as string}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
