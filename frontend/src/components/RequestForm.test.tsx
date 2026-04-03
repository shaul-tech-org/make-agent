import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import RequestForm from "./RequestForm";

// Mock the api module
vi.mock("../api", () => ({
  api: {
    sendRequest: vi.fn(),
  },
}));

import { api } from "../api";
const mockSendRequest = vi.mocked(api.sendRequest);

describe("RequestForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("렌더링", () => {
    it("제목이 표시된다", () => {
      render(<RequestForm />);
      expect(screen.getByText("Request")).toBeInTheDocument();
    });

    it("입력 필드가 표시된다", () => {
      render(<RequestForm />);
      expect(screen.getByPlaceholderText("요청을 입력하세요...")).toBeInTheDocument();
    });

    it("Send 버튼이 표시된다", () => {
      render(<RequestForm />);
      expect(screen.getByText("Send")).toBeInTheDocument();
    });

    it("초기에는 결과가 표시되지 않는다", () => {
      render(<RequestForm />);
      expect(screen.queryByText("Complexity:")).not.toBeInTheDocument();
    });
  });

  describe("입력 동작", () => {
    it("텍스트 입력이 가능하다", () => {
      render(<RequestForm />);
      const input = screen.getByPlaceholderText("요청을 입력하세요...");
      fireEvent.change(input, { target: { value: "로그인 API 만들어줘" } });
      expect(input).toHaveValue("로그인 API 만들어줘");
    });

    it("빈 입력으로 제출하면 API를 호출하지 않는다", async () => {
      render(<RequestForm />);
      const button = screen.getByText("Send");
      fireEvent.click(button);
      expect(mockSendRequest).not.toHaveBeenCalled();
    });

    it("공백만 있는 입력은 제출되지 않는다", async () => {
      render(<RequestForm />);
      const input = screen.getByPlaceholderText("요청을 입력하세요...");
      fireEvent.change(input, { target: { value: "   " } });
      fireEvent.click(screen.getByText("Send"));
      expect(mockSendRequest).not.toHaveBeenCalled();
    });
  });

  describe("제출 동작", () => {
    it("요청을 제출하면 API를 호출한다", async () => {
      mockSendRequest.mockResolvedValueOnce({
        request: "로그인 API",
        category: "implementation",
        complexity: "simple",
        agent: "be-developer",
        delegation_plan: null,
      });

      render(<RequestForm />);
      const input = screen.getByPlaceholderText("요청을 입력하세요...");
      fireEvent.change(input, { target: { value: "로그인 API" } });
      fireEvent.click(screen.getByText("Send"));

      expect(mockSendRequest).toHaveBeenCalledWith("로그인 API");
    });

    it("로딩 중 버튼이 비활성화된다", async () => {
      mockSendRequest.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      render(<RequestForm />);
      const input = screen.getByPlaceholderText("요청을 입력하세요...");
      fireEvent.change(input, { target: { value: "테스트" } });
      fireEvent.click(screen.getByText("Send"));

      const button = screen.getByRole("button");
      expect(button).toBeDisabled();
    });
  });

  describe("결과 표시", () => {
    it("단순 요청 결과를 표시한다", async () => {
      mockSendRequest.mockResolvedValueOnce({
        request: "로그인 API",
        category: "implementation",
        complexity: "simple",
        agent: "be-developer",
        delegation_plan: null,
      });

      render(<RequestForm />);
      fireEvent.change(screen.getByPlaceholderText("요청을 입력하세요..."), {
        target: { value: "로그인 API" },
      });
      fireEvent.click(screen.getByText("Send"));

      await waitFor(() => {
        expect(screen.getByText("simple")).toBeInTheDocument();
      });
      expect(screen.getByText("be-developer")).toBeInTheDocument();
      expect(screen.getByText("implementation")).toBeInTheDocument();
    });

    it("simple 복잡도는 success 클래스를 가진다", async () => {
      mockSendRequest.mockResolvedValueOnce({
        request: "test",
        category: "implementation",
        complexity: "simple",
        agent: "be-developer",
        delegation_plan: null,
      });

      render(<RequestForm />);
      fireEvent.change(screen.getByPlaceholderText("요청을 입력하세요..."), {
        target: { value: "test" },
      });
      fireEvent.click(screen.getByText("Send"));

      await waitFor(() => {
        const el = screen.getByText("simple");
        expect(el.className).toContain("text-success");
      });
    });

    it("complex 복잡도는 error 클래스를 가진다", async () => {
      mockSendRequest.mockResolvedValueOnce({
        request: "test",
        category: "implementation",
        complexity: "complex",
        agent: "ceo",
        delegation_plan: {
          ceo_tasks: [],
          cto_tasks: [],
          phases: [],
          agent_summary: [],
        },
      });

      render(<RequestForm />);
      fireEvent.change(screen.getByPlaceholderText("요청을 입력하세요..."), {
        target: { value: "test" },
      });
      fireEvent.click(screen.getByText("Send"));

      await waitFor(() => {
        const el = screen.getByText("complex");
        expect(el.className).toContain("text-error");
      });
    });

    it("위임 계획이 있으면 표시한다", async () => {
      mockSendRequest.mockResolvedValueOnce({
        request: "사용자 관리",
        category: "implementation",
        complexity: "complex",
        agent: "ceo",
        delegation_plan: {
          ceo_tasks: [
            { id: 1, name: "DB 설계", type: "backend", depends_on: [] },
          ],
          cto_tasks: [],
          phases: [{ phase: 1, tasks: ["DB 설계"], parallel: false }],
          agent_summary: [{ agent: "be-developer", task_count: 1 }],
        },
      });

      render(<RequestForm />);
      fireEvent.change(screen.getByPlaceholderText("요청을 입력하세요..."), {
        target: { value: "사용자 관리" },
      });
      fireEvent.click(screen.getByText("Send"));

      await waitFor(() => {
        expect(screen.getByText("Delegation Plan")).toBeInTheDocument();
      });
      expect(screen.getAllByText(/DB 설계/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText("Phase 1")).toBeInTheDocument();
    });
  });

  describe("에러 처리", () => {
    it("API 에러 시 결과를 초기화한다", async () => {
      mockSendRequest.mockRejectedValueOnce(new Error("500"));

      render(<RequestForm />);
      fireEvent.change(screen.getByPlaceholderText("요청을 입력하세요..."), {
        target: { value: "에러 테스트" },
      });
      fireEvent.click(screen.getByText("Send"));

      await waitFor(() => {
        expect(screen.queryByText("Complexity:")).not.toBeInTheDocument();
      });
    });
  });
});
