'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  CheckCircle, 
  X, 
  Eye,
  Database,
  GitBranch,
  FileText
} from 'lucide-react'

interface Proposal {
  id: string
  type: string
  payload: any
  status: string
  created_at: string
}

interface ProposalsViewerProps {
  onRefresh?: () => void
}

export function ProposalsViewer({ onRefresh }: ProposalsViewerProps) {
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProposals()
  }, [])

  const fetchProposals = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/proposals`)
      if (response.ok) {
        const data = await response.json()
        setProposals(data.proposals || [])
      }
    } catch (error) {
      console.error('Failed to fetch proposals:', error)
    } finally {
      setLoading(false)
    }
  }

  const approveProposal = async (proposalId: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/proposals/${proposalId}/approve`,
        { method: 'POST' }
      )
      
      if (response.ok) {
        // Refresh proposals list
        await fetchProposals()
        onRefresh?.()
      }
    } catch (error) {
      console.error('Failed to approve proposal:', error)
    }
  }

  const rejectProposal = async (proposalId: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/proposals/${proposalId}/reject`,
        { method: 'POST' }
      )
      
      if (response.ok) {
        await fetchProposals()
      }
    } catch (error) {
      console.error('Failed to reject proposal:', error)
    }
  }

  const getProposalIcon = (type: string) => {
    switch (type) {
      case 'entity':
        return <Database className="h-4 w-4 text-blue-500" />
      case 'relation':
        return <GitBranch className="h-4 w-4 text-green-500" />
      case 'instance':
        return <FileText className="h-4 w-4 text-purple-500" />
      default:
        return <Eye className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Ontology Proposals</CardTitle>
          <CardDescription>Loading proposals...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Ontology Proposals</CardTitle>
        <CardDescription>
          Review and approve proposed ontology extensions from uploaded documents
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {proposals.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No proposals available. Upload documents to generate ontology proposals.
            </div>
          ) : (
            proposals.map((proposal) => (
              <div key={proposal.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getProposalIcon(proposal.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium capitalize">{proposal.type}</h4>
                        <Badge className={getStatusColor(proposal.status)}>
                          {proposal.status}
                        </Badge>
                      </div>
                      <div className="mt-2 text-sm text-muted-foreground">
                        <pre className="whitespace-pre-wrap font-mono text-xs bg-gray-50 p-2 rounded">
                          {JSON.stringify(proposal.payload, null, 2)}
                        </pre>
                      </div>
                      <div className="mt-2 text-xs text-muted-foreground">
                        Created: {new Date(proposal.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  
                  {proposal.status === 'pending' && (
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => approveProposal(proposal.id)}
                        className="text-green-600 hover:text-green-700"
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => rejectProposal(proposal.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="h-4 w-4 mr-1" />
                        Reject
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
        
        {proposals.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <Button variant="outline" onClick={fetchProposals}>
              Refresh Proposals
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
