'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatNumber } from '@/lib/utils'
import { TrendingUp, TrendingDown, LucideIcon } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: number | string
  description: string
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  isLoading?: boolean
  variant?: 'default' | 'secondary'
  className?: string
}

export function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  isLoading = false,
  variant = 'default',
  className
}: MetricCardProps) {
  if (isLoading) {
    return (
      <Card className={cn('metric-card', className)}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-4" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-16 mb-1" />
          <Skeleton className="h-3 w-24" />
        </CardContent>
      </Card>
    )
  }

  const formattedValue = typeof value === 'number' ? formatNumber(value) : value

  return (
    <Card className={cn(
      'metric-card transition-all duration-200 hover:shadow-lg',
      variant === 'secondary' && 'bg-muted/50',
      className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className={cn(
          'h-4 w-4',
          variant === 'default' ? 'text-kudwa-500' : 'text-muted-foreground'
        )} />
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline space-x-2">
          <div className="text-2xl font-bold">
            {formattedValue}
          </div>
          {trend && (
            <div className={cn(
              'flex items-center text-xs font-medium',
              trend.isPositive ? 'text-financial-profit' : 'text-financial-loss'
            )}>
              {trend.isPositive ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1" />
              )}
              {trend.value}%
            </div>
          )}
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          {description}
        </p>
      </CardContent>
    </Card>
  )
}
