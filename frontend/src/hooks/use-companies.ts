import { useQuery } from "@tanstack/react-query";
import { getCompanies } from "@/lib/api";
import type { Company } from "@/lib/companies";

export function useCompanies() {
  return useQuery<Company[]>({
    queryKey: ["companies"],
    queryFn: getCompanies,
    staleTime: 5 * 60 * 1000,
  });
}
