'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  BarChart3, 
  Plus, 
  Grid3X3, 
  Layout,
  PieChart,
  TrendingUp,
  Table,
  Calendar,
  Target,
  Zap
} from 'lucide-react'

export default function CanvasPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard Canvas</h1>
          <p className="text-muted-foreground">
            Custom dashboard builder with drag-and-drop widgets
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="default" className="bg-blue-100 text-blue-800 hover:bg-blue-100 dark:bg-blue-900 dark:text-blue-100">
            <Layout className="mr-1 h-3 w-3" />
            Design Mode
          </Badge>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Widget
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Canvas Area */}
        <div className="lg:col-span-3">
          <div className="space-y-4">
            {/* Widget Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Sample Widget 1 */}
              <Card className="group hover:shadow-lg transition-all duration-200 border-2 border-dashed border-transparent hover:border-blue-200">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">Revenue Overview</CardTitle>
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button variant="ghost" size="sm">
                        <Grid3X3 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="h-32 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/50 dark:to-cyan-950/50 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <BarChart3 className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground">Chart Widget</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Sample Widget 2 */}
              <Card className="group hover:shadow-lg transition-all duration-200 border-2 border-dashed border-transparent hover:border-green-200">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">Key Metrics</CardTitle>
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button variant="ghost" size="sm">
                        <Grid3X3 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Total Revenue</span>
                      <span className="font-semibold text-green-600">$124,567</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Active Users</span>
                      <span className="font-semibold">2,847</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Conversion</span>
                      <span className="font-semibold text-blue-600">3.2%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Full Width Widget */}
            <Card className="group hover:shadow-lg transition-all duration-200 border-2 border-dashed border-transparent hover:border-purple-200">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium">Transaction Timeline</CardTitle>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="sm">
                      <Grid3X3 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-48 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/50 dark:to-pink-950/50 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <TrendingUp className="h-12 w-12 text-purple-500 mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Timeline Widget</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Add Widget Area */}
            <Card className="border-2 border-dashed border-muted-foreground/25 hover:border-muted-foreground/50 transition-colors">
              <CardContent className="flex items-center justify-center h-32">
                <Button variant="outline" className="flex items-center space-x-2">
                  <Plus className="h-4 w-4" />
                  <span>Add New Widget</span>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Widget Library */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Widget Library</CardTitle>
              <CardDescription className="text-xs">
                Drag widgets to canvas
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <Button variant="outline" size="sm" className="h-16 flex-col">
                  <BarChart3 className="h-4 w-4 mb-1" />
                  <span className="text-xs">Chart</span>
                </Button>
                <Button variant="outline" size="sm" className="h-16 flex-col">
                  <PieChart className="h-4 w-4 mb-1" />
                  <span className="text-xs">Pie Chart</span>
                </Button>
                <Button variant="outline" size="sm" className="h-16 flex-col">
                  <Table className="h-4 w-4 mb-1" />
                  <span className="text-xs">Table</span>
                </Button>
                <Button variant="outline" size="sm" className="h-16 flex-col">
                  <Target className="h-4 w-4 mb-1" />
                  <span className="text-xs">KPI</span>
                </Button>
                <Button variant="outline" size="sm" className="h-16 flex-col">
                  <Calendar className="h-4 w-4 mb-1" />
                  <span className="text-xs">Calendar</span>
                </Button>
                <Button variant="outline" size="sm" className="h-16 flex-col">
                  <Zap className="h-4 w-4 mb-1" />
                  <span className="text-xs">Activity</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Layout Options</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Grid3X3 className="mr-2 h-4 w-4" />
                Grid Layout
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Layout className="mr-2 h-4 w-4" />
                Free Layout
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Canvas Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Widgets</span>
                <span className="font-medium">3</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Layout</span>
                <span className="font-medium">Grid</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Auto-save</span>
                <span className="font-medium text-green-600">On</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
