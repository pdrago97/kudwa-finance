-- Enable pgvector
create extension if not exists vector;

-- Drop old POC tables
DROP TABLE IF EXISTS kudwa_widgets CASCADE;
DROP TABLE IF EXISTS kudwa_proposals CASCADE;
DROP TABLE IF EXISTS kudwa_instances CASCADE;
DROP TABLE IF EXISTS kudwa_ontology_relations CASCADE;
DROP TABLE IF EXISTS kudwa_ontology_entities CASCADE;
DROP TABLE IF EXISTS kudwa_vectors CASCADE;
DROP TABLE IF EXISTS kudwa_chunks CASCADE;
DROP TABLE IF EXISTS kudwa_files CASCADE;
DROP TABLE IF EXISTS kudwa_conversations CASCADE;
DROP TABLE IF EXISTS kudwa_messages CASCADE;

-- Files
CREATE TABLE kudwa_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text,
  filename text NOT NULL,
  mime text,
  size_bytes bigint,
  sha256 text,
  source text,
  created_at timestamptz DEFAULT now(),
  status text DEFAULT 'received'
);

-- Chunks
CREATE TABLE kudwa_chunks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  file_id uuid REFERENCES kudwa_files(id) ON DELETE CASCADE,
  chunk_index int,
  content text,
  meta jsonb DEFAULT '{}'::jsonb
);

-- Vectors (pgvector)
CREATE TABLE kudwa_vectors (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chunk_id uuid REFERENCES kudwa_chunks(id) ON DELETE CASCADE,
  embedding vector(1536)
);
CREATE INDEX ON kudwa_vectors USING ivfflat (embedding vector_cosine_ops);

-- Ontology entities and relations
CREATE TABLE kudwa_ontology_entities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  properties jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE kudwa_ontology_relations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_entity_id uuid REFERENCES kudwa_ontology_entities(id) ON DELETE CASCADE,
  target_entity_id uuid REFERENCES kudwa_ontology_entities(id) ON DELETE CASCADE,
  rel_type text NOT NULL,
  properties jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- Instances (records)
CREATE TABLE kudwa_instances (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id uuid REFERENCES kudwa_ontology_entities(id) ON DELETE SET NULL,
  properties jsonb DEFAULT '{}'::jsonb,
  source_file_id uuid REFERENCES kudwa_files(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now()
);

-- Proposals (human-in-the-loop)
CREATE TABLE kudwa_proposals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  type text NOT NULL, -- entity | relation | instance | property
  payload jsonb NOT NULL,
  status text NOT NULL DEFAULT 'pending', -- pending | approved | rejected
  created_by text,
  created_at timestamptz DEFAULT now(),
  reviewed_by text,
  reviewed_at timestamptz,
  merge_result jsonb
);
CREATE INDEX ON kudwa_proposals(status);

-- Widgets
CREATE TABLE kudwa_widgets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text,
  title text,
  layout text, -- 'half' | 'full'
  spec jsonb,
  created_at timestamptz DEFAULT now()
);

-- Chat memory (optional)
CREATE TABLE kudwa_conversations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE kudwa_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id uuid REFERENCES kudwa_conversations(id) ON DELETE CASCADE,
  role text, -- user | assistant | system
  content text,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

