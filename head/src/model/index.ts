// 项目大了，TS还是必要的，不然传什么类型，返回什么东西都不知道，后面的人维护更头疼
// 小项目就可以随意点~

/**
 * 分页返回接口
 */
export interface PageResult<T> {
  /**
   * 分页结果
   */
  recordList: T;
  /**
   * 总数
   */
  count: number;
}
/**
 * 结果返回接口
 */
export interface Result<T> {
  /**
   * 返回状态
   */
  flag: boolean;
  /**
   * 状态码
   */
  code: number;
  /**
   * 返回信息
   */
  msg: string;
  /**
   * 返回数据
   */
  data: T;
}

/**
 * 分页参数
 */
export interface PageQuery {
  /**
   * 当前页
   */
  current: number;
  /**
   * 每页大小
   */
  size: number;
}

/**
 * 上传图片
 */
export interface Picture {
  /**
   * 链接
   */
  url: string;
}

/**
 * 审核DTO
 */
export interface CheckDTO {
  /**
   * id集合
   */
  idList: number[];
  /**
   * 是否通过 (0否 1是)
   */
  isCheck: number;
}

/**
 * 标签类型
 */
export interface Label {
  id: string;
  class: string;
  cf: string;
  x1: string;
  y1: string;
  x2: string;
  y2: string;
}