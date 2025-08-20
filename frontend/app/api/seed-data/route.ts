import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function POST(request: NextRequest) {
  try {
    console.log('Seeding sample data...')
    
    // Create admin client with service role key
    const supabaseAdmin = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!,
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false
        }
      }
    )
    
    // Sample entities to add
    const sampleEntities = [
      {
        name: 'Acme Corporation',
        properties: {
          type: 'Company',
          industry: 'Technology',
          employees: '500+',
          revenue: '$50M'
        }
      },
      {
        name: 'John Smith',
        properties: {
          type: 'Person',
          role: 'CEO',
          department: 'Executive',
          company: 'Acme Corporation'
        }
      },
      {
        name: 'Payment Processing System',
        properties: {
          type: 'Transaction',
          amount: '$25,000',
          status: 'Active',
          frequency: 'Monthly'
        }
      },
      {
        name: 'Q4 Financial Report',
        properties: {
          type: 'Report',
          period: 'Q4 2024',
          status: 'Published',
          pages: '45'
        }
      }
    ]
    
    // Insert entities
    const { data: entities, error: entitiesError } = await supabaseAdmin
      .from('kudwa_ontology_entities')
      .insert(sampleEntities)
      .select()
    
    if (entitiesError) {
      console.error('Error inserting entities:', entitiesError)
      throw entitiesError
    }
    
    // Create some sample relations if we have entities
    if (entities && entities.length >= 2) {
      const sampleRelations = [
        {
          source_entity_id: entities[0].id, // Company
          target_entity_id: entities[1].id, // Person
          rel_type: 'employs'
        },
        {
          source_entity_id: entities[1].id, // Person
          target_entity_id: entities[2].id, // Transaction
          rel_type: 'manages'
        },
        {
          source_entity_id: entities[0].id, // Company
          target_entity_id: entities[3].id, // Report
          rel_type: 'publishes'
        }
      ]
      
      const { error: relationsError } = await supabaseAdmin
        .from('kudwa_ontology_relations')
        .insert(sampleRelations)
      
      if (relationsError) {
        console.error('Error inserting relations:', relationsError)
        throw relationsError
      }
    }
    
    console.log('Sample data seeded successfully')
    
    return NextResponse.json({ 
      success: true, 
      message: 'Sample data has been added successfully',
      entitiesAdded: entities?.length || 0
    })
  } catch (error) {
    console.error('Error seeding data:', error)
    return NextResponse.json(
      { success: false, message: 'Failed to seed data: ' + (error as Error).message },
      { status: 500 }
    )
  }
}
