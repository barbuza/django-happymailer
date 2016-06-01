from happymailer import Template, Layout


class BasicLayout(Layout):
    name = 'basic'
    description = 'basic layout'
    content = '''
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-text padding-left="0" padding-right="0"/>
      <mj-divider border-width="1px" border-color="#ccc"/>
    </mj-attributes>
  </mj-head>
  <mj-body>
    <mj-container>
      {{ body }}
      <mj-section>
        <mj-column>
          <mj-social display="google facebook" text-mode="false"/>
        </mj-column>
      </mj-section>
    </mj-container>
  </mj-body>
</mjml>
    '''


class WelcomeTemplate(Template):
    name = 'welcome'
    layout = 'base'
    variables = {}
