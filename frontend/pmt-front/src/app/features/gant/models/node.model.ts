interface Node {
  count: number;
  next?: any;
  previous?: any;
  results: Result[];
}

interface Result {
  id: number;
  created: string;
  updated: string;
  name: string;
  description?: any;
  closed?: any;
  creator: number;
  parent?: number;
  status: number;
  childtype: number;
  assignee?: any;
  defaultbaseline?: number;
}
