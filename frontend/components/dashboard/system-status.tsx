'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Activity,
  Server,
  Database,
  Wifi
} from 'lucide-react'

interface SystemStatusProps {
  health: number
  isLoading?: boolean
}

export function SystemStatus({ health, isLoading = false }: SystemStatusProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            System Status
          </CardTitle>
          <CardDescription>Current system health</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-2 w-full" />
          </div>
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-5 w-16" />
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  const getHealthStatus = (health: number) => {
    if (health >= 95) return { status: 'Excellent', color: 'success', icon: CheckCircle }
    if (health >= 80) return { status: 'Good', color: 'warning', icon: AlertTriangle }
    return { status: 'Poor', color: 'destructive', icon: XCircle }
  }

  const { status, color, icon: StatusIcon } = getHealthStatus(health)

  // Mock service statuses
  const services = [
    { name: 'API Server', status: 'online', icon: Server },
    { name: 'Database', status: 'online', icon: Database },
    { name: 'Network', status: 'online', icon: Wifi },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Activity className="h-5 w-5 mr-2" />
          System Status
        </CardTitle>
        <CardDescription>Current system health</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Overall Health */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Overall Health</span>
            <Badge variant={color} className="flex items-center">
              <StatusIcon className="h-3 w-3 mr-1" />
              {status}
            </Badge>
          </div>
          <Progress value={health} className="h-2" />
          <p className="text-xs text-muted-foreground">{health}% operational</p>
        </div>

        {/* Service Status */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Services</h4>
          {services.map((service) => (
            <div key={service.name} className="flex items-center justify-between">
              <div className="flex items-center">
                <service.icon className="h-4 w-4 mr-2 text-muted-foreground" />
                <span className="text-sm">{service.name}</span>
              </div>
              <Badge 
                variant={service.status === 'online' ? 'success' : 'destructive'}
                className="text-xs"
              >
                {service.status}
              </Badge>
            </div>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="pt-2 border-t">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-financial-profit">99.9%</p>
              <p className="text-xs text-muted-foreground">Uptime</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-kudwa-500">2.3s</p>
              <p className="text-xs text-muted-foreground">Response</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
