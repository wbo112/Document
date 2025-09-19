spring boot  web启动全流程

`AutoConfigurationImportSelector`的`process`方法会去加载配置文件`AutoConfiguration`的内容。

```

		@Override
		public void process(AnnotationMetadata annotationMetadata, DeferredImportSelector deferredImportSelector) {
			Assert.state(deferredImportSelector instanceof AutoConfigurationImportSelector,
					() -> String.format("Only %s implementations are supported, got %s",
							AutoConfigurationImportSelector.class.getSimpleName(),
							deferredImportSelector.getClass().getName()));
			// 加载AutoConfiguration的内容
			AutoConfigurationEntry autoConfigurationEntry = ((AutoConfigurationImportSelector) deferredImportSelector)
					.getAutoConfigurationEntry(annotationMetadata);
			this.autoConfigurationEntries.add(autoConfigurationEntry);
			for (String importClassName : autoConfigurationEntry.getConfigurations()) {
				this.entries.putIfAbsent(importClassName, annotationMetadata);
			}
		}
```

具体加载的内容在`\spring-boot-autoconfigure-2.5.1.jar!\META-INF\spring.factories`中`key`=`org.springframework.boot.autoconfigure.EnableAutoConfiguration`的部分。

### 1、DispatcherServletAutoConfiguration

具体看到会加载一个`org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration`的配置类。



在加载`org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration`时，会扫描到它内部定义的bean。加载`DispatcherServlet`、`DispatcherServletRegistrationBean`.

```
		@Bean(name = DEFAULT_DISPATCHER_SERVLET_BEAN_NAME)
		public DispatcherServlet dispatcherServlet(WebMvcProperties webMvcProperties) {
			DispatcherServlet dispatcherServlet = new DispatcherServlet();
			dispatcherServlet.setDispatchOptionsRequest(webMvcProperties.isDispatchOptionsRequest());
			dispatcherServlet.setDispatchTraceRequest(webMvcProperties.isDispatchTraceRequest());
			dispatcherServlet.setThrowExceptionIfNoHandlerFound(webMvcProperties.isThrowExceptionIfNoHandlerFound());
			dispatcherServlet.setPublishEvents(webMvcProperties.isPublishRequestHandledEvents());
			dispatcherServlet.setEnableLoggingRequestDetails(webMvcProperties.isLogRequestDetails());
			return dispatcherServlet;
		}
```

```
		@Bean(name = DEFAULT_DISPATCHER_SERVLET_REGISTRATION_BEAN_NAME)
		@ConditionalOnBean(value = DispatcherServlet.class, name = DEFAULT_DISPATCHER_SERVLET_BEAN_NAME)
		public DispatcherServletRegistrationBean dispatcherServletRegistration(DispatcherServlet dispatcherServlet,
				WebMvcProperties webMvcProperties, ObjectProvider<MultipartConfigElement> multipartConfig) {
			DispatcherServletRegistrationBean registration = new DispatcherServletRegistrationBean(dispatcherServlet,
					webMvcProperties.getServlet().getPath());
			registration.setName(DEFAULT_DISPATCHER_SERVLET_BEAN_NAME);
			registration.setLoadOnStartup(webMvcProperties.getServlet().getLoadOnStartup());
			multipartConfig.ifAvailable(registration::setMultipartConfig);
			return registration;
		}
```



在`tomcat`的启动过程中，会配置`TomcatServletWebServerFactory`,`prepareContext`方法会将

```
protected void prepareContext(Host host, ServletContextInitializer[] initializers) {
		File documentRoot = getValidDocumentRoot();
		TomcatEmbeddedContext context = new TomcatEmbeddedContext();
		if (documentRoot != null) {
			context.setResources(new LoaderHidingResourceRoot(context));
		}
		context.setName(getContextPath());
		context.setDisplayName(getDisplayName());
		context.setPath(getContextPath());
		File docBase = (documentRoot != null) ? documentRoot : createTempDir("tomcat-docbase");
		context.setDocBase(docBase.getAbsolutePath());
		context.addLifecycleListener(new FixContextListener());
		context.setParentClassLoader((this.resourceLoader != null) ? this.resourceLoader.getClassLoader()
				: ClassUtils.getDefaultClassLoader());
		resetDefaultLocaleMapping(context);
		addLocaleMappings(context);
		try {
			context.setCreateUploadTargets(true);
		}
		catch (NoSuchMethodError ex) {
			// Tomcat is < 8.5.39. Continue.
		}
		configureTldPatterns(context);
		WebappLoader loader = new WebappLoader();
		loader.setLoaderClass(TomcatEmbeddedWebappClassLoader.class.getName());
		loader.setDelegate(true);
		context.setLoader(loader);
		if (isRegisterDefaultServlet()) {
			addDefaultServlet(context);
		}
		if (shouldRegisterJspServlet()) {
			addJspServlet(context);
			addJasperInitializer(context);
		}
		context.addLifecycleListener(new StaticResourceConfigurer(context));
		// 配置ServletContextInitializer
		ServletContextInitializer[] initializersToUse = mergeInitializers(initializers);
		host.addChild(context);
		// 配置到tomcat中,tomcat启动时就会调用到
		configureContext(context, initializersToUse);
		postProcessContext(context);
	}

```

具体是通过`TomcatStarter`的构造方法传入，后续`tomcat`在启动过程中会调用到`TomcatStarter`的`onStartup`方法进行处理。

继而调用到`ServletWebServerApplicationContext`的`selfInitialize`方法，加载第一步创建的`dispatcherServlet`到`ServletContext`中。

```
	private void selfInitialize(ServletContext servletContext) throws ServletException {
		prepareWebApplicationContext(servletContext);
		registerApplicationScope(servletContext);
		WebApplicationContextUtils.registerEnvironmentBeans(getBeanFactory(), servletContext);
		// getServletContextInitializerBeans()方法会在容器中查找`ServletContextInitializer.class`类型的bean,进行加载。
		// 就能获取到第一步创建的bean dispatcherServletRegistration,加载dispatcherServlet
		for (ServletContextInitializer beans : getServletContextInitializerBeans()) {
			beans.onStartup(servletContext);
		}
	}
```

`ServletContextInitializerBeans`这个类就能看到这个类加载的东西还是比较多的

```
	private void addServletContextInitializerBean(String beanName, ServletContextInitializer initializer,
			ListableBeanFactory beanFactory) {
		if (initializer instanceof ServletRegistrationBean) {
			Servlet source = ((ServletRegistrationBean<?>) initializer).getServlet();
			addServletContextInitializerBean(Servlet.class, beanName, initializer, beanFactory, source);
		}
		else if (initializer instanceof FilterRegistrationBean) {
			Filter source = ((FilterRegistrationBean<?>) initializer).getFilter();
			addServletContextInitializerBean(Filter.class, beanName, initializer, beanFactory, source);
		}
		else if (initializer instanceof DelegatingFilterProxyRegistrationBean) {
			String source = ((DelegatingFilterProxyRegistrationBean) initializer).getTargetBeanName();
			addServletContextInitializerBean(Filter.class, beanName, initializer, beanFactory, source);
		}
		else if (initializer instanceof ServletListenerRegistrationBean) {
			EventListener source = ((ServletListenerRegistrationBean<?>) initializer).getListener();
			addServletContextInitializerBean(EventListener.class, beanName, initializer, beanFactory, source);
		}
		else {
			addServletContextInitializerBean(ServletContextInitializer.class, beanName, initializer, beanFactory,
					initializer);
		}
	}

```







上面已经加载了`servlet`,下面看下如何加载`controller`的

上面说的加载`\spring-boot-autoconfigure-2.5.1.jar!\META-INF\spring.factories`中`key`=`org.springframework.boot.autoconfigure.EnableAutoConfiguration`的部分时，也会加载

具体看到会加载一个`org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration`的类。

会加载`RequestMappingHandlerMapping`这个bean。

```

		@Bean
		@Primary
		@Override
		public RequestMappingHandlerMapping requestMappingHandlerMapping(
				@Qualifier("mvcContentNegotiationManager") ContentNegotiationManager contentNegotiationManager,
				@Qualifier("mvcConversionService") FormattingConversionService conversionService,
				@Qualifier("mvcResourceUrlProvider") ResourceUrlProvider resourceUrlProvider) {
			// Must be @Primary for MvcUriComponentsBuilder to work
			return super.requestMappingHandlerMapping(contentNegotiationManager, conversionService,
					resourceUrlProvider);
		}

```

在加载`RequestMappingHandlerMapping`这个bean后，会调用到它的`afterPropertiesSet`方法，调用到父类的`initHandlerMethods`,在这里会获取容器中的所有bean的类型，查看是否有`Controller.class`,`RequestMapping.class`注解

```
	protected void initHandlerMethods() {
		for (String beanName : getCandidateBeanNames()) {
			if (!beanName.startsWith(SCOPED_TARGET_NAME_PREFIX)) {
				processCandidateBean(beanName);
			}
		}
		handlerMethodsInitialized(getHandlerMethods());
	}

```

···

```
protected void processCandidateBean(String beanName) {
    Class<?> beanType = null;
    try {
       beanType = obtainApplicationContext().getType(beanName);
    }
    catch (Throwable ex) {
       // An unresolvable bean type, probably from a lazy bean - let's ignore it.
       if (logger.isTraceEnabled()) {
          logger.trace("Could not resolve type for bean '" + beanName + "'", ex);
       }
    }
    if (beanType != null && isHandler(beanType)) {
       detectHandlerMethods(beanName);
    }
}
```



在上面的`detectHandlerMethods(beanName)`中 ，就会加载`controller`中定义的方法,代码是在`AbstractHandlerMethodMapping`中，具体如下

```
	/**
	 * Look for handler methods in the specified handler bean.
	 * @param handler either a bean name or an actual handler instance
	 * @see #getMappingForMethod
	 */
	protected void detectHandlerMethods(Object handler) {
		Class<?> handlerType = (handler instanceof String ?
				obtainApplicationContext().getType((String) handler) : handler.getClass());

		if (handlerType != null) {
			Class<?> userType = ClassUtils.getUserClass(handlerType);
			Map<Method, T> methods = MethodIntrospector.selectMethods(userType,
					(MethodIntrospector.MetadataLookup<T>) method -> {
						try {
						// 在这里,将有RequestMapping注解的方法创建一个RequestMappingInfo
							return getMappingForMethod(method, userType);
						}
						catch (Throwable ex) {
							throw new IllegalStateException("Invalid mapping on handler class [" +
									userType.getName() + "]: " + method, ex);
						}
					});
			if (logger.isTraceEnabled()) {
				logger.trace(formatMappings(userType, methods));
			}
			else if (mappingsLogger.isDebugEnabled()) {
				mappingsLogger.debug(formatMappings(userType, methods));
			}
			methods.forEach((method, mapping) -> {
				Method invocableMethod = AopUtils.selectInvocableMethod(method, userType);
				// 在这里，将上面找到的method添加到集合中
				registerHandlerMethod(handler, invocableMethod, mapping);
			});
		}
	}

```

```
	protected void registerHandlerMethod(Object handler, Method method, T mapping) {
		this.mappingRegistry.register(mapping, handler, method);
	}

```

这里就已经将controller加载了  

