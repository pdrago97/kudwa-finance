import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function POST(request: NextRequest) {
  try {
    console.log('Resetting all data...')

    // Check if we have the required environment variables
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
      console.warn('Supabase configuration missing, simulating reset')
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate delay
      return NextResponse.json({
        success: true,
        message: 'Data reset simulated (Supabase not configured)'
      })
    }

    // Create admin client with service role key
    const supabaseAdmin = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.SUPABASE_SERVICE_KEY,
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false
        }
      }
    )

    // Reset ontology tables first (relations depend on entities)
    const { error: relationsError } = await supabaseAdmin
      .from('kudwa_ontology_relations')
      .delete()
      .neq('id', '00000000-0000-0000-0000-000000000000') // Delete all

    if (relationsError) {
      console.error('Error deleting relations:', relationsError)
      throw relationsError
    }

    const { error: entitiesError } = await supabaseAdmin
      .from('kudwa_ontology_entities')
      .delete()
      .neq('id', '00000000-0000-0000-0000-000000000000') // Delete all

    if (entitiesError) {
      console.error('Error deleting entities:', entitiesError)
      throw entitiesError
    }

    // Reset other related tables
    const tablesToReset = [
      'kudwa_documents',
      'kudwa_files',
      'kudwa_chunks',
      'kudwa_embeddings',
      'kudwa_vectors',
      'kudwa_instances',
      'kudwa_messages',
      'kudwa_conversations',
      'kudwa_financial_observations',
      'kudwa_financial_time_series',
      'kudwa_financial_datasets',
      'kudwa_widgets'
    ]

    for (const table of tablesToReset) {
      try {
        await supabaseAdmin
          .from(table)
          .delete()
          .neq('id', '00000000-0000-0000-0000-000000000000')
        console.log(`Reset table: ${table}`)
      } catch (error) {
        console.warn(`Could not reset table ${table}:`, error)
        // Continue with other tables even if one fails
      }
    }

    console.log('Data reset completed successfully')

    return NextResponse.json({
      success: true,
      message: 'All data has been reset successfully'
    })
  } catch (error) {
    console.error('Error resetting data:', error)
    return NextResponse.json(
      { success: false, message: 'Failed to reset data: ' + (error as Error).message },
      { status: 500 }
    )
  }
}
