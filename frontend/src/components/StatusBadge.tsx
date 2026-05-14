import { statusTone } from "../utils/status";

type StatusBadgeProps = {
  value: string;
};

export function StatusBadge({ value }: StatusBadgeProps) {
  return <span className={`status-badge ${statusTone(value)}`}>{value}</span>;
}

