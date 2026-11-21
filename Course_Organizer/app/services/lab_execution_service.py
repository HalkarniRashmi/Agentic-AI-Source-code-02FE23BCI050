
"""
Central execution service for AcademicFlow Agentic AI Labs.

This module provides the lab catalogue and will serve as the
single entry point for professor-triggered lab execution.
"""

from datetime import datetime


class LabExecutionService:

    LABS = [
        {
            "id": 2,
            "title": "Tool-Using Agent",
            "category": "Agent Tools",
            "description": (
                "Uses registered academic tools to retrieve "
                "notes, assignments, submissions and milestones."
            ),
            "concepts": [
                "Tool Registry",
                "Tool Selection",
                "Database Operations"
            ]
        },
        {
            "id": 3,
            "title": "Reusable Academic Skills",
            "category": "Agent Skills",
            "description": (
                "Demonstrates reusable academic skills through "
                "the existing Skill Registry."
            ),
            "concepts": [
                "Skill Registry",
                "Reusable Skills",
                "Context Injection"
            ]
        },
        {
            "id": 4,
            "title": "Memory and Retrieval",
            "category": "Agent Memory",
            "description": (
                "Retrieves relevant academic context and "
                "conversation memory for a professor."
            ),
            "concepts": [
                "Memory Retrieval",
                "Context Building",
                "Keyword Matching"
            ]
        },
        {
            "id": 5,
            "title": "MCP Connectors",
            "category": "MCP Integration",
            "description": (
                "Connects AcademicFlow to its MCP server "
                "and discovers registered academic tools."
            ),
            "concepts": [
                "Model Context Protocol",
                "MCP Client",
                "MCP Server"
            ]
        },
        {
            "id": 6,
            "title": "Agent Runtime",
            "category": "Agent Runtime",
            "description": (
                "Executes specialist agents through the "
                "Central Agent and records execution details."
            ),
            "concepts": [
                "Central Agent",
                "Specialist Agents",
                "Execution Tracking"
            ]
        },
        {
            "id": 7,
            "title": "Agentic Node Graph",
            "category": "Workflow Orchestration",
            "description": (
                "Builds and executes a multi-node academic "
                "workflow using the existing workflow engine."
            ),
            "concepts": [
                "Workflow Nodes",
                "Directed Graph",
                "Workflow Execution"
            ]
        },
        {
            "id": 8,
            "title": "Parallel Agent Swarm",
            "category": "Multi-Agent Systems",
            "description": (
                "Executes independent academic agent tasks "
                "concurrently using a parallel agent swarm."
            ),
            "concepts": [
                "Parallel Execution",
                "ThreadPoolExecutor",
                "Multi-Agent Coordination"
            ]
        },
        {
            "id": 9,
            "title": "Deep Research Agent",
            "category": "Research Agent",
            "description": (
                "Organizes and synthesizes evidence from "
                "sources supplied to the agent."
            ),
            "concepts": [
                "Evidence Collection",
                "Source Analysis",
                "Research Synthesis"
            ]
        },
        {
            "id": 10,
            "title": "Cloud Operations Agent",
            "category": "Cloud Operations",
            "description": (
                "Analyzes application logs and identifies "
                "potential operational incidents."
            ),
            "concepts": [
                "Log Analysis",
                "Incident Classification",
                "Remediation Recommendations"
            ]
        },
        {
            "id": 11,
            "title": "Agentic SDLC",
            "category": "Software Engineering",
            "description": (
                "Generates structured software development "
                "lifecycle stages from a requirement."
            ),
            "concepts": [
                "Requirements",
                "SDLC",
                "Quality Checks"
            ]
        },
        {
            "id": 12,
            "title": "Safety and Governance",
            "category": "AI Governance",
            "description": (
                "Evaluates actions against role permissions "
                "and governance restrictions."
            ),
            "concepts": [
                "Role-Based Access",
                "Safety Checks",
                "Governance"
            ]
        },
        {
            "id": 13,
            "title": "Engineering Analysis Agent",
            "category": "Engineering AI",
            "description": (
                "Analyzes supplied engineering readings "
                "and identifies threshold anomalies."
            ),
            "concepts": [
                "Sensor Data Analysis",
                "Statistical Analysis",
                "Anomaly Detection"
            ]
        },
        {
            "id": 14,
            "title": "Capstone Project Studio",
            "category": "Agentic Integration",
            "description": (
                "Coordinates multiple specialist agents "
                "within one integrated capstone workflow."
            ),
            "concepts": [
                "Agent Orchestration",
                "Multi-Agent Integration",
                "Execution Trace"
            ]
        }
    ]

    @classmethod
    def get_labs(cls):
        """Return the available lab catalogue."""

        return {
            "success": True,
            "total_labs": len(cls.LABS),
            "labs": cls.LABS
        }

    @classmethod
    def get_lab(cls, lab_id):
        """Find a lab using its ID."""

        for lab in cls.LABS:
            if lab["id"] == lab_id:
                return lab

        return None
    @classmethod
    def execute_lab(cls, lab_id, professor_id, parameters=None):
        """
        Execute an existing lab using the authenticated professor's ID.
        """

        parameters = parameters or {}

        lab = cls.get_lab(lab_id)

        if lab is None:
            raise ValueError("Invalid lab ID.")

        if not isinstance(professor_id, int) or professor_id <= 0:
            raise ValueError("Valid professor identity is required.")

        started_at = datetime.now()

        try:
            result = cls._dispatch(
                lab_id,
                professor_id,
                parameters
            )

            return {
                "success": True,
                "lab": lab,
                "execution": {
                    "status": "completed",
                    "started_at": started_at.isoformat(),
                    "completed_at": datetime.now().isoformat()
                },
                "result": result
            }

        except Exception as error:
            return {
                "success": False,
                "lab": lab,
                "execution": {
                    "status": "failed",
                    "started_at": started_at.isoformat(),
                    "completed_at": datetime.now().isoformat()
                },
                "error": str(error)
            }

    @staticmethod
    def _dispatch(lab_id, professor_id, parameters):

        from app.services.course_service import CourseService
        from app.services.project_service import ProjectService

        courses = CourseService.list_professor_courses(professor_id)
        projects = ProjectService.get_professor_projects(professor_id)

        course_id = (
            parameters.get("course_id")
            or (courses[0]["id"] if courses else None)
        )

        project_id = (
            parameters.get("project_id")
            or (projects[0]["id"] if projects else None)
        )

        context = {
            "user_id": professor_id,
            "role": "professor"
        }

        # LAB 2 — TOOL USING AGENT
        if lab_id == 2:

            from app.tools.academic_tools import (
                build_academic_tool_registry
            )

            registry = build_academic_tool_registry()

            results = {
                "registered_tools": registry.list_tools(),
                "course_retrieval": registry.execute_tool(
                    "list_courses",
                    context
                ),
                "notes_retrieval": registry.execute_tool(
                    "list_notes",
                    context
                )
            }

            if course_id:
                results["assignment_retrieval"] = (
                    registry.execute_tool(
                        "list_assignments",
                        {
                            **context,
                            "course_id": course_id
                        }
                    )
                )

            if project_id:
                results["milestone_retrieval"] = (
                    registry.execute_tool(
                        "list_milestones",
                        {
                            **context,
                            "project_id": project_id
                        }
                    )
                )

            return results

        # LAB 3 — REUSABLE ACADEMIC SKILLS
        if lab_id == 3:

            from app.skills.academic_skills import (
                build_academic_skill_registry
            )

            registry = build_academic_skill_registry()

            results = {
                "registered_skills": registry.list_skills()
            }

            if course_id:
                results["assignment_overview"] = registry.execute(
                    "assignment_overview",
                    context,
                    {"course_id": course_id}
                )

            results["student_grade_permission_test"] = {
                "expected": "Permission denied for professor",
                "status": "not_executed"
            }

            try:
                registry.execute(
                    "student_grade_review",
                    context,
                    {}
                )
            except PermissionError as error:
                results["student_grade_permission_test"] = {
                    "status": "passed",
                    "message": str(error)
                }

            return results

        # LAB 4 — MEMORY AND RETRIEVAL
        if lab_id == 4:

            from app.services.memory_retrieval_service import (
                MemoryRetrievalService
            )

            query = parameters.get(
                "query",
                "Show my academic courses, notes and assignments."
            )

            if not isinstance(query, str) or not query.strip():
                raise ValueError("A retrieval query is required.")

            return MemoryRetrievalService.build_retrieval_context(
                user_id=professor_id,
                role="professor",
                query=query,
                conversation_id=parameters.get("conversation_id"),
                top_k=5
            )

        # LAB 5 — MCP CONNECTORS
        if lab_id == 5:

            import asyncio
            import sys

            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            async def execute_mcp():

                server = StdioServerParameters(
                    command=sys.executable,
                    args=[
                        "-m",
                        "app.connectors.academic_mcp_server"
                    ]
                )

                async with stdio_client(server) as (read, write):
                    async with ClientSession(read, write) as session:

                        await session.initialize()

                        tools = await session.list_tools()

                        available = [
                            tool.name for tool in tools.tools
                        ]

                        if "list_notes" not in available:
                            raise RuntimeError(
                                "MCP list_notes tool was not discovered."
                            )

                        response = await session.call_tool(
                            "list_notes",
                            arguments={
                                "user_id": professor_id,
                                "role": "professor"
                            }
                        )

                        return {
                            "server": "AcademicFlow MCP Server",
                            "discovered_tools": available,
                            "executed_tool": "list_notes",
                            "response": [
                                getattr(item, "text", str(item))
                                for item in response.content
                            ]
                        }

            return asyncio.run(execute_mcp())

        # LAB 6 — AGENT RUNTIME
        if lab_id == 6:

            from app.agents.central_agent import CentralAgent
            from app.services.agent_runtime_service import (
                AgentRuntimeService
            )

            coordinator = CentralAgent()

            result = coordinator.run({
                "task": "notes",
                **context
            })

            return {
                "registered_agents": coordinator.get_registered_agents(),
                "agent_result": result,
                "recent_execution_logs": (
                    AgentRuntimeService.get_recent_executions(limit=10)
                )
            }

        # LAB 7 — AGENTIC NODE GRAPH
        if lab_id == 7:

            if not course_id:
                raise ValueError(
                    "Create a course before executing this workflow."
                )

            from app.labs.lab07_agentic_node_graph import (
                build_academic_workflow
            )
            from app.workflows.workflow_engine import WorkflowEngine

            graph = build_academic_workflow()

            result = WorkflowEngine().execute(
                graph,
                {
                    **context,
                    "course_id": course_id
                }
            )

            return {
                "workflow_nodes": list(graph.nodes.keys()),
                "workflow_edges": graph.edges,
                "execution_result": result
            }

        # LAB 8 — PARALLEL AGENT SWARM
        if lab_id == 8:

            from app.agents.parallel_agent_swarm import (
                ParallelAgentSwarm
            )

            tasks = [
                {
                    "task": "notes",
                    **context
                }
            ]

            if course_id:
                tasks.append({
                    "task": "assignments",
                    "action": "list",
                    **context,
                    "course_id": course_id
                })

            if project_id:
                tasks.append({
                    "task": "milestones",
                    **context,
                    "project_id": project_id
                })

            return ParallelAgentSwarm(
                max_workers=3
            ).execute(tasks)

        # LAB 9 — DEEP RESEARCH
        if lab_id == 9:

            from app.labs.lab09_deep_research import (
                DeepResearchAgent
            )

            topic = parameters.get("topic")
            sources = parameters.get("sources", [])

            if not topic:
                raise ValueError("Enter a research topic.")

            return DeepResearchAgent().run(topic, sources)

        # LAB 10 — CLOUD OPERATIONS
        if lab_id == 10:

            from app.labs.lab10_cloud_operations import (
                CloudOperationsAgent
            )

            logs = parameters.get("logs")

            if not logs:
                raise ValueError("Provide application logs to analyze.")

            return CloudOperationsAgent().analyze_logs(logs)

        # LAB 11 — AGENTIC SDLC
        if lab_id == 11:

            from app.labs.lab11_agentic_sdlc import (
                AgenticSDLCFactory
            )

            requirement = parameters.get("requirement")

            if not requirement:
                raise ValueError("Provide a software requirement.")

            return AgenticSDLCFactory().run(requirement)

        # LAB 12 — SAFETY AND GOVERNANCE
        if lab_id == 12:

            from app.labs.lab12_safety_governance import (
                SafetyGovernanceAgent
            )

            action = parameters.get("action", "view_academic_data")

            return SafetyGovernanceAgent().evaluate(
                role="professor",
                action=action,
                input_data=parameters.get("input_data")
            )

        # LAB 13 — ENGINEERING ANALYSIS
        if lab_id == 13:

            from app.labs.lab13_engineering_agent import (
                EngineeringAgent
            )

            readings = parameters.get("readings")

            if not isinstance(readings, list) or not readings:
                raise ValueError(
                    "Provide a non-empty list of numeric readings."
                )

            return EngineeringAgent().analyze(
                readings,
                threshold=parameters.get("threshold", 80)
            )

        # LAB 14 — CAPSTONE PROJECT STUDIO
        if lab_id == 14:

            from app.labs.lab14_capstone_studio import (
                CapstoneProjectStudio
            )

            return CapstoneProjectStudio().run()

        raise ValueError("No execution handler exists for this lab.")
