---
title: "Writing User Stories and Requirements"
date: 2024-09-18T09:03:53-07:00
draft: false
author: Anton Golubtsov
summary:
---

Recently I was reading though a bunch of technical designs and I've noticed a common mistake when it comes to
writing user-stories and requirements - assuming a solution. The biggest issue for me when I write requirements myself is that than whenever I include a part of a solution I'm thinking about into the requirements it limits my ability to innovate since I'm bound to a specific solution. In many cases I observed improvements in my designs when I was focused on what the customer needs rather on fulfilling requirement tied to my first and probably not a bright idea.

Another advantage of not assuming a solution, at least for me, that it helps me to include a broader context and consider the customer needs a few steps before, after, and the customer is trying to achieve at a higher level. This sometimes completely changes the way I think about the problem.

I asked ChatGPT to help me articulate those ideas in clearer way and here is what I've got from it.

---

### **1. Focus on the User's Needs, Not the Solution**

**Explain:**

-   **User stories and requirements should capture what the user needs and why**, not how to implement it.
-   This keeps the team focused on delivering value to the user without being constrained by predetermined solutions.

**Example of a Requirement Specifying a Solution (Not Ideal):**

-   _"The application shall use a drop-down menu for users to select their country."_

**Rewritten Requirement Without Specifying a Solution:**

-   _"The application shall allow users to easily select their country during registration."_

**Why This Matters:**

-   Avoiding specific solutions opens the door for designers and developers to find the most user-friendly and efficient method, such as an auto-complete field or a map selection, which might be more appropriate.

---

### **2. Encourage Innovation and Expertise**

**Explain:**

-   **Teams bring diverse expertise**; prescribing solutions can limit their ability to innovate.
-   Allowing flexibility can lead to better, more efficient solutions that stakeholders might not have considered.

**Example of a User Story Specifying a Solution (Not Ideal):**

-   _"As a user, I want to receive notifications via SMS using Twilio API so that I can stay updated."_

**Rewritten User Story Without Specifying a Solution:**

-   _"As a user, I want to receive timely notifications so that I can stay updated."_

**Why This Matters:**

-   The team can explore various notification methods (email, push notifications, SMS) and choose the best technology stack, possibly finding more cost-effective or robust solutions than the one originally specified.

---

### **3. Maintain Flexibility for Changing Requirements**

**Explain:**

-   **Technology and project scopes evolve**; non-solution-specific requirements are more adaptable to change.
-   This reduces the need for frequent revisions to the requirements documents.

**Example of a Requirement Specifying a Solution (Not Ideal):**

-   _"The system shall store data in an Oracle database."_

**Rewritten Requirement Without Specifying a Solution:**

-   _"The system shall securely store data and allow for efficient retrieval and scalability."_

**Why This Matters:**

-   The development team can select the most appropriate database technology (SQL, NoSQL, cloud-based solutions) based on current needs and future scalability.

---

### **4. Prevent Over-Engineering and Resource Waste**

**Explain:**

-   **Specifying solutions can lead to unnecessary complexity**, increasing development time and costs.
-   It may force the team to implement a solution that doesn't integrate well with other system components.

**Example of a Requirement Specifying a Solution (Not Ideal):**

-   _"The report must be generated in PDF format using Adobe Acrobat SDK."_

**Rewritten Requirement Without Specifying a Solution:**

-   _"The system shall provide reports that users can easily view and download."_

**Why This Matters:**

-   Developers might find that HTML or CSV formats better meet user needs or that a different library offers improved performance or easier maintenance.

---

### **5. Enhance Collaboration and Ownership**

**Explain:**

-   **Clear boundaries between 'what' and 'how' foster better collaboration.**
-   Stakeholders define the problem; the development team devises the solution, promoting ownership and accountability.

**Example of a Requirement Specifying a Solution (Not Ideal):**

-   _"Implement a caching mechanism using Redis to improve performance."_

**Rewritten Requirement Without Specifying a Solution:**

-   _"The system shall perform user queries within two seconds under normal load conditions."_

**Why This Matters:**

-   The team can explore various optimization techniques, not just caching, to meet performance requirements.

---

### **Why Following This Approach Is Important**

1. **Leverages Team Expertise:**

    - Developers and designers can use their skills to find the best solutions.

2. **Improves User Satisfaction:**

    - Solutions are tailored to user needs, enhancing the user experience.

3. **Increases Project Agility:**

    - Easier to adapt to changes in technology or user requirements.

4. **Reduces Miscommunication:**

    - Clear, concise requirements minimize misunderstandings.

5. **Optimizes Resources:**
    - Prevents unnecessary work on specified solutions that may not be optimal.

---

### **Conclusion**

By focusing on what the user needs rather than how to deliver it, you empower your development team to create more effective, innovative, and efficient solutions. This approach:

-   **Enhances Flexibility:** Adapts to new information or changes in project scope.
-   **Encourages Best Practices:** Allows the use of the latest technologies and methodologies.
-   **Strengthens Team Dynamics:** Promotes trust and better collaboration between stakeholders and the development team.
