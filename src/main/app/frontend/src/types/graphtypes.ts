export interface AssistantNode {
  content: string;
  fastRPSimilarity: number[];
  id: string;
  numDocs: number;
  postTime: Date;
  rating: string;
  responseCommunity: number;
  role: string;
  similarityPR: number;
  vectorIndexSearch: boolean;
}

export interface ConversationNode {
  badMessagesCount: number;
  goodMessagesCount: number;
  conversationLength: number;
  id: string;
  llm: string;
  temperature: number;
}

export interface DocumentNode {
  community: number;
  contextCount: number;
  embedding: number[];
  fastRPSimilarity: number[];
  index: number;
  pageRank: number;
  text: string;
  url: string;
}

export interface SessionNode {
  conversationCount: number;
  createTime: Date;
  sessionId: string;
}

export interface MessageNode {
  content: string;
  embedding: number[];
  id: string;
  postTime: Date;
  role: string;
}

export interface ConversationRelationship {
  startNode: ConversationNode;
  endNode: MessageNode;
}

export interface MessageRelationship {
  startNode: MessageNode;
  endNode: AssistantNode;
}

export interface AssistantRelationship {
  startNode: AssistantNode;
  endNode: DocumentNode;
}

export interface ConversationEntry {
  assistantNodesDocumentPath: AssistantNode[];
  documentNodes: DocumentNode[];
  conversationNodes: ConversationNode[];
  messageNodes: MessageNode[];
  assistantNodesMessagePath: AssistantNode[];
}

export interface GraphResponse {
  conversationEntries: ConversationEntry[];
}
