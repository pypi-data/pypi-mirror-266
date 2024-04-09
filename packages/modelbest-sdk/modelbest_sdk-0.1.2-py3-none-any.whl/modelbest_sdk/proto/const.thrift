// 特殊字符
const string LINE_SEP = "\n"
const string ROLE_CONTENT_SEP = "："
const string START_INDICATOR = "<|im_start|>"
const string END_INDICATOR = "<|im_end|>"
const string SYSTEM_INDICATOR = "system"
const string ASSISTANT_INDICATOR = "assistant"
const string USER_INDICATOR = "user"
const string KNOWLEDGE_INDICATOR = "knowledge"

// prompt拼接字段
const string PROMPT_0 = "现在请你假扮"
const string PROMPT_1 = "与我进行对话"
const string PROMPT_2 = "接下来的对话里，你需要扮演"
const string PROMPT_3 = "我将扮演："
const string PROMPT_4 = "我们的关系是："
const string PROMPT_5 = "[开始对话]"
const string RAG_PROMPT = "下面会给你提供一段背景知识，请你在回答之前参考这段知识进行回答。"

// prompt大框架需要固定
const string BASIC_INFO_TEXT = "基本信息"
const string PERSONALITY_TEXT = "的性格"
const string RELATIONSHIP_TEXT = "人物关系"
const string EXPERIENCE_TEXT = "的主要经历"
const string LANG_STYLE_TEXT = "的语言风格"
const string RELATED_PEOPLE_TEXT = "相关人物"
const string STORY_TEXT = "故事梗概"