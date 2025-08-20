import { NextRequest, NextResponse } from 'next/server'
import { ontologyService } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    console.log('Testing Supabase connection...')
    console.log('Environment variables:')
    console.log('NEXT_PUBLIC_SUPABASE_URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
    console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY (first 20 chars):', process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.substring(0, 20))
    console.log('SUPABASE_SERVICE_KEY (first 20 chars):', process.env.SUPABASE_SERVICE_KEY?.substring(0, 20))

    const entities = await ontologyService.getEntities()
    const relations = await ontologyService.getRelations()
    const stats = await ontologyService.getStats()

    console.log('Entities found:', entities.length)
    console.log('Relations found:', relations.length)
    console.log('Stats:', stats)

    return NextResponse.json({
      success: true,
      data: {
        entities: entities.length,
        relations: relations.length,
        stats,
        sampleEntities: entities.slice(0, 3),
        sampleRelations: relations.slice(0, 3)
      },
      debug: {
        hasUrl: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
        hasAnonKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
        hasServiceKey: !!process.env.SUPABASE_SERVICE_KEY,
        anonKeyPrefix: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.substring(0, 20),
        serviceKeyPrefix: process.env.SUPABASE_SERVICE_KEY?.substring(0, 20)
      }
    })
  } catch (error) {
    console.error('Supabase test error:', error)
    return NextResponse.json(
      { success: false, error: (error as Error).message },
      { status: 500 }
    )
  }
}
