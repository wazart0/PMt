export class Task {
  public expanded = false;
  constructor(
    public Name: string,
    public Resource: string,
    public Start: Date,
    public Finish: Date,
    public children: Task[]
  ) {}
}
