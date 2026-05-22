"""Bugzilla API client"""

import base64
import os
from typing import Any
import httpx


class Bugzilla:
    """Bugzilla API class"""

    def __init__(self, url: str, api_key: str):
        self.api_url: str = url + "/rest"
        self.base_url: str = url
        self.api_key: str = api_key
        # request params sent for each request
        self.params: dict[str, Any] = {"api_key": self.api_key}
        # Create a shared async client
        self.client: httpx.AsyncClient = httpx.AsyncClient()

    async def bug_info(self, bug_id: int) -> dict[str, Any]:
        """get information about a given bug"""

        r = await self.client.get(url=f"{self.api_url}/bug/{bug_id}", params=self.params)

        if r.status_code != 200:
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        return r.json()["bugs"][0]

    async def bug_comments(self, bug_id: int) -> dict[str, Any]:
        """Get comments of a bug"""

        r = await self.client.get(url=f"{self.api_url}/bug/{bug_id}/comment", params=self.params)

        if r.status_code != 200:
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        return r.json()["bugs"][f"{bug_id}"]["comments"]

    async def add_comment(
        self, bug_id: int, comment: str, is_private: bool
    ) -> dict[str, int]:
        """Add a comment to bug, which can optionally be private"""

        c = {"comment": comment, "is_private": is_private}

        r = await self.client.post(
            url=f"{self.api_url}/bug/{bug_id}/comment", params=self.params, json=c
        )

        if r.status_code != 201:
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        return r.json()

    async def download_attachments(
        self, bug_id: int, dest_dir: str | None = None
    ) -> list[dict[str, Any]]:
        """Download all attachments for a specific bug to a temporary directory.

        Args:
            bug_id: The ID of the bug.
            dest_dir: Optional destination directory. If not specified, a 'tmp'
                      directory in the project root will be used.

        Returns:
            A list of dicts containing attachment metadata and the local path:
            [{"id": 123, "file_name": "...", "path": "...", "size": 1024}]
        """
        r = await self.client.get(
            url=f"{self.api_url}/bug/{bug_id}/attachment", params=self.params
        )

        if r.status_code != 200:
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        data = r.json()
        bugs_data = data.get("bugs", {})
        attachments = (
            bugs_data.get(str(bug_id)) or bugs_data.get(bug_id) or []
        )

        if dest_dir is None:
            # Create a tmp directory in the project root
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            dest_dir = os.path.join(project_root, "tmp")

        os.makedirs(dest_dir, exist_ok=True)

        downloaded = []
        for att in attachments:
            att_id = att.get("id")
            file_name = att.get("file_name")
            b64_data = att.get("data")

            if not b64_data:
                continue

            try:
                file_content = base64.b64decode(b64_data)
            except Exception as e:
                raise ValueError(f"Failed to decode attachment {att_id}: {e}")

            # Construct safe filename
            safe_file_name = os.path.basename(file_name)
            safe_file_name = f"{att_id}_{safe_file_name}"
            dest_path = os.path.join(dest_dir, safe_file_name)

            with open(dest_path, "wb") as f:
                f.write(file_content)

            downloaded.append(
                {
                    "id": att_id,
                    "bug_id": bug_id,
                    "file_name": file_name,
                    "content_type": att.get("content_type"),
                    "size": att.get("size"),
                    "path": dest_path,
                }
            )

        return downloaded

    async def download_attachment(
        self, attachment_id: int, dest_dir: str | None = None
    ) -> dict[str, Any]:
        """Download a specific attachment by its ID.

        Args:
            attachment_id: The ID of the attachment.
            dest_dir: Optional destination directory. If not specified, a 'tmp'
                      directory in the project root will be used.

        Returns:
            A dict containing attachment metadata and the local path:
            {"id": 123, "file_name": "...", "path": "...", "size": 1024}
        """
        r = await self.client.get(
            url=f"{self.api_url}/bug/attachment/{attachment_id}",
            params=self.params,
        )

        if r.status_code != 200:
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        data = r.json()
        attachments_data = data.get("attachments", {})
        att = attachments_data.get(str(attachment_id)) or attachments_data.get(
            attachment_id
        )

        if not att:
            raise ValueError(f"Attachment {attachment_id} not found in response")

        b64_data = att.get("data")
        if not b64_data:
            raise ValueError(f"No data field found in attachment {attachment_id}")

        if dest_dir is None:
            # Create a tmp directory in the project root
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            dest_dir = os.path.join(project_root, "tmp")

        os.makedirs(dest_dir, exist_ok=True)

        try:
            file_content = base64.b64decode(b64_data)
        except Exception as e:
            raise ValueError(f"Failed to decode attachment {attachment_id}: {e}")

        file_name = att.get("file_name")
        safe_file_name = os.path.basename(file_name)
        safe_file_name = f"{attachment_id}_{safe_file_name}"
        dest_path = os.path.join(dest_dir, safe_file_name)

        with open(dest_path, "wb") as f:
            f.write(file_content)

        return {
            "id": attachment_id,
            "bug_id": att.get("bug_id"),
            "file_name": file_name,
            "content_type": att.get("content_type"),
            "size": att.get("size"),
            "path": dest_path,
        }

    async def bugs_info(self, bug_ids: list[int]) -> list[dict[str, Any]]:
        """get information about multiple bugs in a single request"""
        if not bug_ids:
            return []

        # Join ids with commas
        ids_str = ",".join(map(str, bug_ids))
        params = self.params.copy()
        params["id"] = ids_str

        r = await self.client.get(url=f"{self.api_url}/bug", params=params)

        if r.status_code != 200:
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        return r.json().get("bugs", [])

    async def bugs_comments(self, bug_ids: list[int]) -> dict[str, list[dict[str, Any]]]:
        """fetch comments for multiple bugs in parallel using asyncio.gather"""
        if not bug_ids:
            return {}

        import asyncio

        async def fetch_one(bug_id: int):
            try:
                comments = await self.bug_comments(bug_id)
                return str(bug_id), comments
            except Exception:
                return str(bug_id), []

        tasks = [fetch_one(bid) for bid in bug_ids]
        results = await asyncio.gather(*tasks)
        return dict(results)

    async def bugs_analysis_context(self, bug_ids: list[int]) -> dict[str, Any]:
        """Gather bug info and comment previews in parallel to return a prompt-friendly analysis payload"""
        if not bug_ids:
            return {}

        # Fetch all bug details in a single request
        try:
            info_list = await self.bugs_info(bug_ids)
        except Exception as e:
            raise httpx.TransportError(f"Failed to gather batch bug info: {e}")

        # Fetch comments in parallel
        comments_dict = await self.bugs_comments(bug_ids)

        # Merge them into a structured dict mapping bug_id -> merged details
        merged = {}
        for info in info_list:
            bid = info.get("id")
            bid_str = str(bid)
            comments = comments_dict.get(bid_str, [])

            # Limit comments to most relevant to avoid token explosion
            comments_preview = []
            if len(comments) <= 4:
                comments_preview = comments
            else:
                comments_preview = (
                    comments[:2]
                    + [
                        {
                            "text": f"... [{len(comments)-4} comments omitted] ...",
                            "is_private": False,
                            "creator": "System",
                        }
                    ]
                    + comments[-2:]
                )

            merged[bid_str] = {
                "id": bid,
                "product": info.get("product"),
                "component": info.get("component"),
                "summary": info.get("summary"),
                "status": info.get("status"),
                "resolution": info.get("resolution"),
                "assigned_to": info.get("assigned_to"),
                "creator": info.get("creator"),
                "last_change_time": info.get("last_change_time"),
                "severity": info.get("severity"),
                "priority": info.get("priority"),
                "comments_count": len(comments),
                "comments_preview": comments_preview,
            }

        return merged

    async def close(self):
        """Close the async client"""
        await self.client.aclose()

