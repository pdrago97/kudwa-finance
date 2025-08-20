import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function GET(request: NextRequest) {
  try {
    console.log('Testing direct Supabase connection...')
    
    // Use the service role key you provided directly
    const supabaseUrl = 'https://zafvnssmznpeurboybnd.supabase.co'
    const serviceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphZnZuc3Ntem5wZXVyYm95Ym5kIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTA1NTA5OSwiZXhwIjoyMDY0NjMxMDk5fQ.f5x48--VC61Oiis-XhfIXNGa1hVwlXbpVEo2ahNKPkY'
    
    console.log('Creating Supabase client with direct keys...')
    console.log('URL:', supabaseUrl)
    console.log('Service Key (first 20 chars):', serviceKey.substring(0, 20))
    
    const supabase = createClient(supabaseUrl, serviceKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    })
    
    console.log('Attempting to fetch entities...')
    const { data: entities, error: entitiesError } = await supabase
      .from('kudwa_ontology_entities')
      .select('*')
      .limit(5)
    
    console.log('Entities response - data:', entities?.length, 'error:', entitiesError)
    
    console.log('Attempting to fetch relations...')
    const { data: relations, error: relationsError } = await supabase
      .from('kudwa_ontology_relations')
      .select('*')
      .limit(5)
    
    console.log('Relations response - data:', relations?.length, 'error:', relationsError)
    
    return NextResponse.json({
      success: true,
      data: {
        entities: entities?.length || 0,
        relations: relations?.length || 0,
        sampleEntities: entities?.slice(0, 3) || [],
        sampleRelations: relations?.slice(0, 3) || []
      },
      errors: {
        entitiesError,
        relationsError
      }
    })
  } catch (error) {
    console.error('Direct Supabase test error:', error)
    return NextResponse.json(
      { success: false, error: (error as Error).message },
      { status: 500 }
    )
  }
}
