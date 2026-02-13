import requests
from django.conf import settings


class FlaskAPIClient:
    def __init__(self):
        self.url = settings.FLASK_API_URL
        self.key = settings.FLASK_API_KEY

    def _get_head(self, include_auth=False):
        headers = {"Content-Type": "application/json"}
        if include_auth:
            headers["X-API-KEY"] = self.key
        return headers

    def _handle_response(self, response):
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            try:
                error_data = response.json()
                raise Exception(
                    f"API Error: {error_data.get('error', 'Unknown error')}"
                )
            except:
                raise Exception(f"API Error: HTTP {response.status_code}")
        return response.json()

    def _normalize_story(self, story):
        """Normalize story fields from Flask API to Django expected format"""
        if not story:
            return None
        # tags comes as comma separated string - keep as is
        # author_id may not exist, default to None
        story.setdefault("author_id", None)
        story.setdefault("tags", "")
        story.setdefault("description", "")
        return story

    def _normalize_page(self, page):
        """Normalize page fields - Flask uses 'content', Django expects 'text'"""
        if not page:
            return None
        # Map content -> text
        if "content" in page and "text" not in page:
            page["text"] = page["content"]
        page.setdefault("is_ending", False)
        page.setdefault("ending_label", None)
        # Normalize choices
        if "choices" in page:
            page["choices"] = [self._normalize_choice(c) for c in page["choices"]]
        return page

    def _normalize_choice(self, choice):
        """Normalize choice fields - Flask uses different field names than Django expects"""
        if not choice:
            return None
        # Map from_page_id -> page_id
        if "from_page_id" in choice and "page_id" not in choice:
            choice["page_id"] = choice["from_page_id"]
        # Map to_page_id -> next_page_id
        if "to_page_id" in choice and "next_page_id" not in choice:
            choice["next_page_id"] = choice["to_page_id"]
        # Map choice_text -> text
        if "choice_text" in choice and "text" not in choice:
            choice["text"] = choice["choice_text"]
        return choice

    # READ ENDPOINTS

    def get_stories(self, status=None, search=None, tags=None):
        params = {}
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        if tags:
            params["tags"] = tags

        try:
            response = requests.get(
                f"{self.url}/stories", params=params, timeout=10
            )
            data = self._handle_response(response)
            if not data:
                return []
            return [self._normalize_story(s) for s in data]
        except Exception as e:
            print(f"Error fetching stories: {e}")
            return []

    def get_story(self, story_id, include_pages=False):
        try:
            params = {"include_pages": "true"} if include_pages else {}
            response = requests.get(
                f"{self.url}/stories/{story_id}", params=params, timeout=10
            )
            story = self._handle_response(response)
            if not story:
                return None
            story = self._normalize_story(story)
            # Normalize pages if included
            if include_pages and "pages" in story:
                story["pages"] = [self._normalize_page(p) for p in story["pages"]]
            return story
        except Exception as e:
            print(f"Error fetching story {story_id}: {e}")
            return None

    def get_story_start(self, story_id):
        try:
            response = requests.get(
                f"{self.url}/stories/{story_id}/start", timeout=10
            )
            data = self._handle_response(response)
            if not data:
                return None
            return data
        except Exception as e:
            print(f"Error fetching start of story {story_id}: {e}")
            return None

    def get_page(self, page_id):
        try:
            response = requests.get(f"{self.url}/pages/{page_id}", timeout=10)
            page = self._handle_response(response)
            return self._normalize_page(page)
        except Exception as e:
            print(f"Error fetching page {page_id}: {e}")
            return None

    # WRITE ENDPOINTS

    def create_story(self, title, description="", status="draft", author_id=None, tags=None):
        try:
            # Convert tags list to comma separated string if needed
            if isinstance(tags, list):
                tags = ",".join(tags)

            data = {
                "title": title,
                "description": description,
                "status": status,
                "author_id": author_id,
                "author_name": "Author",
                "tags": tags if tags else "",
            }
            response = requests.post(
                f"{self.url}/stories",
                json=data,
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            result = self._handle_response(response)
            if not result:
                return None
            if isinstance(result, dict) and "story" in result:
                return self._normalize_story(result["story"])
            return self._normalize_story(result)
        except Exception as e:
            print(f"Error creating story: {e}")
            return None

    def update_story(self, story_id, **kwargs):
        try:
            # Convert tags list to comma separated string if needed
            if "tags" in kwargs and isinstance(kwargs["tags"], list):
                kwargs["tags"] = ",".join(kwargs["tags"])

            response = requests.put(
                f"{self.url}/stories/{story_id}",
                json=kwargs,
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            result = self._handle_response(response)
            if not result:
                return None
            if isinstance(result, dict) and "story" in result:
                return self._normalize_story(result["story"])
            return self._normalize_story(result)
        except Exception as e:
            print(f"Error updating story {story_id}: {e}")
            return None

    def delete_story(self, story_id):
        try:
            response = requests.delete(
                f"{self.url}/stories/{story_id}",
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting story {story_id}: {e}")
            return False

    def create_page(self, story_id, text, is_ending=False, ending_label=None):
        try:
            data = {
                "content": text,  # Flask uses 'content' not 'text'
                "is_ending": is_ending,
                "ending_label": ending_label,
            }
            response = requests.post(
                f"{self.url}/stories/{story_id}/pages",
                json=data,
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            result = self._handle_response(response)
            if not result:
                return None
            if isinstance(result, dict) and "page" in result:
                return self._normalize_page(result["page"])
            return self._normalize_page(result)
        except Exception as e:
            print(f"Error creating page: {e}")
            return None

    def update_page(self, page_id, **kwargs):
        try:
            # Map text -> content for Flask API
            if "text" in kwargs:
                kwargs["content"] = kwargs.pop("text")

            response = requests.put(
                f"{self.url}/pages/{page_id}",
                json=kwargs,
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            result = self._handle_response(response)
            if not result:
                return None
            return self._normalize_page(result)
        except Exception as e:
            print(f"Error updating page {page_id}: {e}")
            return None

    def delete_page(self, page_id):
        try:
            response = requests.delete(
                f"{self.url}/pages/{page_id}",
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting page {page_id}: {e}")
            return False

    def create_choice(self, page_id, text, next_page_id):
        try:
            data = {
                "choice_text": text,       # Flask uses 'choice_text'
                "to_page_id": next_page_id,  # Flask uses 'to_page_id'
            }
            response = requests.post(
                f"{self.url}/pages/{page_id}/choices",
                json=data,
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            result = self._handle_response(response)
            if not result:
                return None
            if isinstance(result, dict) and "choice" in result:
                return self._normalize_choice(result["choice"])
            return self._normalize_choice(result)
        except Exception as e:
            print(f"Error creating choice: {e}")
            return None

    def update_choice(self, choice_id, **kwargs):
        try:
            # Map text -> choice_text for Flask API
            if "text" in kwargs:
                kwargs["choice_text"] = kwargs.pop("text")
            # Map next_page_id -> to_page_id for Flask API
            if "next_page_id" in kwargs:
                kwargs["to_page_id"] = kwargs.pop("next_page_id")

            response = requests.put(
                f"{self.url}/choices/{choice_id}",
                json=kwargs,
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            result = self._handle_response(response)
            if not result:
                return None
            return self._normalize_choice(result)
        except Exception as e:
            print(f"Error updating choice {choice_id}: {e}")
            return None

    def delete_choice(self, choice_id):
        try:
            response = requests.delete(
                f"{self.url}/choices/{choice_id}",
                headers=self._get_head(include_auth=True),
                timeout=10,
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting choice {choice_id}: {e}")
            return False


flask_api = FlaskAPIClient()