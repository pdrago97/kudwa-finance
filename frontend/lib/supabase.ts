import { createBrowserClient } from '@supabase/ssr'
import { createClient as createSupabaseClient } from '@supabase/supabase-js'

// Use hardcoded values that we know work
const supabaseUrl = 'https://zafvnssmznpeurboybnd.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphZnZuc3Ntem5wZXVyYm95Ym5kIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTA1NTA5OSwiZXhwIjoyMDY0NjMxMDk5fQ.f5x48--VC61Oiis-XhfIXNGa1hVwlXbpVEo2ahNKPkY'

console.log('Using hardcoded Supabase configuration')
console.log('Supabase URL:', supabaseUrl)
console.log('Supabase Key (first 20 chars):', supabaseAnonKey.substring(0, 20))

// Client-side Supabase client
export const createClient = () => {
  return createBrowserClient(supabaseUrl, supabaseAnonKey)
}

// Direct client for immediate use
export const supabase = createSupabaseClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
})

// Server-side client with service role key (for API routes)
export const supabaseAdmin = createSupabaseClient(
  supabaseUrl,
  supabaseAnonKey, // Using the same working key
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  }
)

// Database types
export interface Database {
  public: {
    Tables: {
      kudwa_entities: {
        Row: {
          id: string
          name: string
          type: string
          properties: any
          created_at: string
          updated_at: string
          user_id: string
        }
        Insert: {
          id?: string
          name: string
          type: string
          properties?: any
          created_at?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          id?: string
          name?: string
          type?: string
          properties?: any
          updated_at?: string
          user_id?: string
        }
      }
      kudwa_relations: {
        Row: {
          id: string
          from_entity: string
          to_entity: string
          relation_type: string
          properties: any
          created_at: string
          updated_at: string
          user_id: string
        }
        Insert: {
          id?: string
          from_entity: string
          to_entity: string
          relation_type: string
          properties?: any
          created_at?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          id?: string
          from_entity?: string
          to_entity?: string
          relation_type?: string
          properties?: any
          updated_at?: string
          user_id?: string
        }
      }
      kudwa_instances: {
        Row: {
          id: string
          entity_id: string
          data: any
          created_at: string
          updated_at: string
          user_id: string
        }
        Insert: {
          id?: string
          entity_id: string
          data: any
          created_at?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          id?: string
          entity_id?: string
          data?: any
          updated_at?: string
          user_id?: string
        }
      }
      kudwa_files: {
        Row: {
          id: string
          filename: string
          mime: string
          size_bytes: number
          sha256: string
          status: string
          created_at: string
          updated_at: string
          user_id: string
        }
        Insert: {
          id?: string
          filename: string
          mime: string
          size_bytes: number
          sha256: string
          status?: string
          created_at?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          id?: string
          filename?: string
          mime?: string
          size_bytes?: number
          sha256?: string
          status?: string
          updated_at?: string
          user_id?: string
        }
      }
      kudwa_proposals: {
        Row: {
          id: string
          type: string
          payload: any
          status: string
          created_by: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          type: string
          payload: any
          status?: string
          created_by: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          type?: string
          payload?: any
          status?: string
          created_by?: string
          updated_at?: string
        }
      }
      kudwa_chat_sessions: {
        Row: {
          id: string
          user_id: string
          title: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          title: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          title?: string
          updated_at?: string
        }
      }
      kudwa_chat_messages: {
        Row: {
          id: string
          session_id: string
          role: 'user' | 'assistant'
          content: string
          metadata: any
          created_at: string
        }
        Insert: {
          id?: string
          session_id: string
          role: 'user' | 'assistant'
          content: string
          metadata?: any
          created_at?: string
        }
        Update: {
          id?: string
          session_id?: string
          role?: 'user' | 'assistant'
          content?: string
          metadata?: any
        }
      }
      kudwa_widgets: {
        Row: {
          id: string
          user_id: string
          dashboard_id: string
          type: string
          config: any
          position: any
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          dashboard_id: string
          type: string
          config: any
          position: any
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          dashboard_id?: string
          type?: string
          config?: any
          position?: any
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}

// Types for our actual ontology data
export interface OntologyEntity {
  id: string
  name: string
  properties: Record<string, any>
  created_at?: string
}

export interface OntologyRelation {
  id: string
  source_entity_id: string
  target_entity_id: string
  rel_type: string
  properties?: Record<string, any>
  created_at?: string
}

// Helper functions for ontology data
export const ontologyService = {
  // Get all entities
  async getEntities(): Promise<OntologyEntity[]> {
    try {
      const { data, error } = await supabase
        .from('kudwa_ontology_entities')
        .select('*')
        .order('created_at', { ascending: false })

      if (error) throw error
      return data || []
    } catch (error) {
      console.error('Error fetching entities:', error)
      return []
    }
  },

  // Get all relations
  async getRelations(): Promise<OntologyRelation[]> {
    try {
      const { data, error } = await supabase
        .from('kudwa_ontology_relations')
        .select('*')
        .order('created_at', { ascending: false })

      if (error) throw error
      return data || []
    } catch (error) {
      console.error('Error fetching relations:', error)
      return []
    }
  },

  // Get entities with their relations for graph visualization
  async getGraphData() {
    const [entities, relations] = await Promise.all([
      this.getEntities(),
      this.getRelations()
    ])

    return { entities, relations }
  },

  // Get statistics
  async getStats() {
    if (!supabase) {
      console.warn('Supabase client not available, using mock data')
      return { entities: 4, relations: 3 }
    }

    try {
      const [entitiesCount, relationsCount] = await Promise.all([
        supabase.from('kudwa_ontology_entities').select('id', { count: 'exact', head: true }),
        supabase.from('kudwa_ontology_relations').select('id', { count: 'exact', head: true })
      ])

      return {
        entities: entitiesCount.count || 0,
        relations: relationsCount.count || 0
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
      return { entities: 4, relations: 3 }
    }
  }
}
