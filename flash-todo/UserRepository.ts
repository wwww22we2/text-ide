// Nullable 类型定义
export type Nullable<T> = T | null;

// User 类型定义（示例）
export interface User {
  id: number;
  name: string;
}

// LogExecutionTime 装饰器
export function LogExecutionTime(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor
): PropertyDescriptor {
  // 这里只是简单返回原始descriptor，实际可扩展为记录执行时间
  return descriptor;
}

// Repository 接口
export interface Repository<T> {
  getById(id: number): Nullable<T>;
}

// UserRepository 实现
export class UserRepository implements Repository<User> {
  private users: User[] = [];

  @LogExecutionTime
  getById(id: number): Nullable<User> {
    return this.users.find((u) => u.id === id) || null;
  }
}